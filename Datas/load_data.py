# -*- coding: utf-8 -*-
"""
@author: Neo
@software: PyCharm
@file: load_data.py
@time: 2023/5/20 19:09
说明:
"""
import datetime
import numpy as np
import pandas as pd
import pymongo
import jqdatasdk as jq
from ShuiDQReport.settings import CLIENT, DATABASE_STAT, DATABASE_BASIC, DATABASE_STRATEGY, DATABASE_BACKTEST
from Utils.utils import trans_str_to_float64, get_screen_size

pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
# 显示所有列
pd.set_option('display.max_columns', None)
# True就是可以换行显示。设置成False的时候不允许换行
pd.set_option('expand_frame_repr', False)


class LoadData(object):
    def __init__(self):
        client = pymongo.MongoClient(CLIENT)
        self.db_stat = client[DATABASE_STAT]
        self.db_stra = client[DATABASE_STRATEGY]
        self.db_basic = client[DATABASE_BASIC]
        self.db_bt = client[DATABASE_BACKTEST]

        self.the_date = None
        self.the_last_date = None
        self.df_industries = None
        self.df_cap = None

        screen_size = get_screen_size()
        self.width1 = int(screen_size[0] * 1 / 3)
        self.width_h = int(screen_size[0] / 2)
        self.width2 = int(screen_size[0] * 2 / 3)
        self.width25 = int(screen_size[0] * 2 / 5)
        self.width3 = int(screen_size[0] * 0.95)
        self.high = self.width1

        self.tmp_dates_chg_df = None

    def _load_trade_records(self, start_date: str, end_date: str, order_type: str):
        if order_type == 'JG':
            table = self.db_stat['delivery_order']
            use_cols = ['发生日期', "证券代码", "证券名称", "业务名称", "成交价格", "成交数量", "成交时间", '成交金额']
        elif order_type == 'DZ':
            table = self.db_stat['statement_of_account']
            use_cols = ['发生日期', "成交时间", "业务名称", "证券代码", "证券名称", "成交价格", "成交金额", "股份余额",
                        '发生金额', '资金本次余额']
        else:
            raise Exception("要不交割单，要不对账单！！！")

        get_cols = dict(zip(use_cols, [1] * len(use_cols)))
        get_cols.update({"_id": 0})

        df = pd.DataFrame(table.find(
            {"发生日期": {'$lte': end_date, '$gte': start_date}}, get_cols, batch_size=100000))
        df.rename(columns={'发生日期': 'date', '证券代码': 'code'}, inplace=True)
        return df

    def load_latest_month_statement_of_account(self, start_date='20230101'):
        """拉对账单"""
        if self.the_date is None:
            self.get_the_date()
        end_date = self.the_date.replace('-', '')
        df = self._load_trade_records(start_date, end_date, order_type='DZ')
        df['date'] = df.date.apply(lambda x: x[:4] + "-" + x[4:6] + "-" + x[-2:])
        df['Date Time'] = df.date + ' ' + df['成交时间']
        df = trans_str_to_float64(df, trans_cols=['成交价格', '成交金额', '股份余额', '发生金额', '资金本次余额', ])
        df.dropna(inplace=True)
        # return df
        return df[df['业务名称'].isin(['证券买入', '证券卖出'])].copy()

    def get_the_date(self):
        dates = list(self.db_stra['factor_weights'].find({}, {"_id": 0, "date": 1}).sort('date', -1).limit(2))
        the_date = dates[0]["date"]
        the_last_date = dates[1]["date"]
        self.the_date = the_date
        self.the_last_date = the_last_date
        return the_date

    def get_industries(self, the_day=None):
        if the_day is None:
            raise Exception("指定日期不能为空呀！！")
        df_ind = pd.DataFrame(self.db_basic['jq_daily_industries'].find(
            {'date': the_day, }, {"_id": 0, "name": 1, "stocks": 1}))
        self.df_industries = df_ind
        return df_ind

    def get_cap_and_log(self, the_day=None):
        if the_day is None:
            raise Exception("指定日期不能为空呀！！")
        df_cap = pd.DataFrame(self.db_basic['w_stocks_daily'].find(
            {'date': the_day, }, {"_id": 0, "code": 1, "market_cap": 1}))
        df_cap['log_market_cap'] = np.log(df_cap['market_cap'])
        df_cap["market_cap"] = (df_cap.market_cap / 100000000).round(1)
        self.df_cap = df_cap
        return df_cap

    def get_trade_loss(self):
        df_loss = pd.DataFrame(self.db_stat['trade_loss_2307'].find({}, {"_id": 0, }))
        df_loss.sort_values('date', inplace=True)
        return df_loss

    def __filter_blacklist(self, df_from, the_day=None):
        if the_day is None:
            raise Exception("指定日期不能为空呀！！")
        df = df_from.copy()
        df_black = pd.DataFrame(self.db_stra['blacklist'].find({'date': the_day}, {"_id": 0, }))
        filtered = df[~df.code.isin(df_black.code.values)]
        return filtered

    def __get_the_factor(self, factor=None, the_day=None, date_s='2022-01-01', date_e='2022-12-31'):
        if factor is None:
            raise Exception("没有指定factor，怎么搞？")
        if the_day is None:
            qds = {"date": {'$gte': date_s, '$lte': date_e}}
        else:
            qds = {'date': the_day}
        if factor == "mv_vol":
            df = pd.DataFrame(self.db_stra['factors_market_rank_snd'].find(
                qds, {"_id": 0, "date": 1, "code": 1, "mv_vol": 1}, batch_size=1000000))
            df = trans_str_to_float64(df, trans_cols=['mv_vol'])
            # 这个因子反向用的
            df.sort_values('mv_vol', ascending=True, inplace=True)
        elif factor == "F_C":
            df = pd.DataFrame(self.db_stra['stocks_FC'].find(qds, {"_id": 0, }, batch_size=1000000).sort('F_c', -1))
            df = trans_str_to_float64(df, trans_cols=['F_c'])
        elif factor == "F1":
            df = pd.DataFrame(self.db_stra['stocks_all'].find(qds, {"_id": 0, }, batch_size=1000000).sort('F1', -1))
            df = trans_str_to_float64(df, trans_cols=['F1'])
        elif factor in ["F_EBIT2P", "F_EPS", "F_NIGttm", "F_ret_com", "F_SalesGttm", "F_cfo2roi", ]:
            df = pd.DataFrame(self.db_stra['factors_apt_and_rank'].find(
                qds, {"_id": 0, "date": 1, "code": 1, factor: 1}, batch_size=1000000))
            df = trans_str_to_float64(df, exp_cols=['date', 'code'])
            # if factor == "F_ret_com":  # 这个因子反向用的
            #     df.sort_values(factor, ascending=True, inplace=True)
            # else:
            #     df.sort_values(factor, ascending=False, inplace=True)
        else:
            raise Exception("指定的因子-->>{}有问题呀".format(factor))
        return df

    def get_chg_factor(self, factor=None):
        """单因子 对应第二天的涨跌幅数据"""
        if factor is None:
            raise Exception("没有指定factor，怎么搞？")
        if self.the_date is None:
            self.get_the_date()
        df_cha = pd.DataFrame(self.db_basic['w_stocks_chg'].find({'date': self.the_date}, {"_id": 0, }))
        df_cha = trans_str_to_float64(df_cha, trans_cols=['chg', ])
        df_factor = self.__get_the_factor(factor=factor, the_day=self.the_last_date)
        df_factor = self.__filter_blacklist(df_factor, the_day=self.the_last_date)
        df = pd.merge(df_factor, df_cha, on="code")
        return df

    def get_about_factor(self, factor=None):
        """单因子 行业、市值"""
        if factor is None:
            raise Exception("没有指定factor，怎么搞？")
        if self.the_date is None:
            self.get_the_date()
        df_factor = self.__get_the_factor(factor=factor, the_day=self.the_date)
        df_factor = self.__filter_blacklist(df_factor, the_day=self.the_date)

        if self.df_industries is None:
            self.get_industries(the_day=self.the_date)
        for row in self.df_industries.itertuples(index=False):
            stocks = eval(getattr(row, "stocks"))
            if len(stocks) > 0:
                ind_name = str(getattr(row, "name"))
                stocks = list(map(lambda x: 'SH' + x[:6] if x.startswith('6') else 'SZ' + x[:6], stocks))
                df_factor.loc[df_factor.code.isin(stocks), 'ind'] = ind_name
        if not df_factor[df_factor.ind.isna()].empty:
            raise Exception("居然没匹配到行业？？？？")
        if self.df_cap is None:
            self.get_cap_and_log(the_day=self.the_date)
        df = pd.merge(df_factor, self.df_cap, on="code")

        return df

    def get_factors_weights(self, F_all=False):
        if F_all:
            df = pd.DataFrame(self.db_stra['factor_weights'].find({}, {"_id": 0, }))
            df.set_index('date', inplace=True)
            cols = [col for col in list(df) if col.startswith("F_")]
            df = trans_str_to_float64(df, trans_cols=cols)
            df = df[cols]
            return df, cols
        else:
            df = pd.DataFrame(self.db_stra['factor_weights'].find({}, {"_id": 0, }).sort('date', -1).limit(1))
            df.set_index('date', inplace=True)
            cols = eval(df.iloc[-1]['factors'])
            df = trans_str_to_float64(df, trans_cols=cols)
            df = df[cols]
            return df.index.values[0], df.iloc[-1].to_dict()

    def get_ics(self, the_factors=True):
        if the_factors:
            factors = dict.fromkeys(self.get_factors_weights()[1], 1)
            factors.update({"_id": 0, "date": 1})
            df_ics = pd.DataFrame(self.db_stra['factor_IC'].find({}, factors))
        else:
            df_ics = pd.DataFrame(self.db_stra['factor_IC'].find({}, {"_id": 0, }))
        df_ics = trans_str_to_float64(df_ics, exp_cols=['date', ])
        df_ics.set_index('date', inplace=True)
        df_ics.sort_index(inplace=True)
        df_IR = pd.DataFrame()
        dates = df_ics[df_ics.index > '2009-01-01'].index.unique().tolist()
        for date in dates:
            data_ics = df_ics.loc[:date]
            IRs = np.sqrt(250) * (data_ics.mean() / data_ics.std())
            dff = abs(pd.DataFrame(IRs).T)
            dff.insert(0, 'date', date)
            df_IR = pd.concat([df_IR, dff])
        df_IR['date'] = pd.to_datetime(df_IR.date)
        return df_ics, df_IR

    def get_cap_and_money_for_strategy(self, stra_name="alpha_one"):
        dict_stra = {"alpha_one": "real_pos_50", "per_2": "real_pos_per_2", "per_2_4": "real_pos_per_2_4"}
        table_name = dict_stra.get(stra_name)
        if table_name is None:
            raise Exception("传入的统计表 {} 名称有误，请检查==>>{}".format(stra_name, dict_stra))
        the_date = list(self.db_bt["real_pos_per_2_4"].find({}, {"_id": 0, "date": 1}).sort('date', -1).limit(1))[0][
            "date"]
        df_bt = pd.DataFrame(self.db_bt[table_name].find({'date': the_date, }, {"_id": 0, }))

        df_cap = pd.DataFrame(self.db_basic['w_stocks_daily'].find(
            {'date': the_date, 'code': {'$in': df_bt.code.to_list()}}, {"_id": 0, "code": 1, "market_cap": 1}))
        df_cap["market_cap"] = (df_cap.market_cap / 100000000).round(1)
        des1 = df_cap.describe()
        des1 = pd.concat([des1, pd.DataFrame({"market_cap": df_cap.market_cap.sum()}, index=["sum", ])])

        df_bt['code_jq'] = df_bt.code.apply(lambda x: x[2:] + ".XSHG" if x[2] == "6" else x[2:] + ".XSHE")
        df_money = pd.DataFrame(self.db_basic['jq_daily_price_pre'].find(
            {'date': the_date, 'code': {'$in': df_bt.code_jq.to_list()}}, {"_id": 0, "code": 1, "money": 1}))
        df_money["money"] = (df_money.money / 10000).round(1)
        des2 = df_money.describe()
        des2 = pd.concat([des2, pd.DataFrame({"money": df_money.money.sum()}, index=["sum", ])])

        des = pd.merge(des1, des2, left_index=True, right_index=True)
        des.reset_index(inplace=True)
        return des, the_date

    def get_bt_strategy(self, stra_name="alpha_one"):
        """回溯 """
        dict_stra = {"alpha_one": "bt_alpha_one", "per_2": "bt_per_2", "per_2_4": "bt_per_2_4"}
        table_name = dict_stra.get(stra_name)
        if table_name is None:
            raise Exception("传入的统计表 {} 名称有误，请检查==>>{}".format(stra_name, dict_stra))
        df = pd.DataFrame(self.db_stat[table_name].find({}, {"_id": 0, }))
        df['net_value'] = (df.stra_chg + 1).cumprod()
        df['net_value5'] = (df.chg5 + 1).cumprod()
        return df

    def get_alpha_one(self):
        """实盘@1"""
        df = pd.DataFrame(self.db_stat['dq_alpha_one'].find(
            {}, {"_id": 0, "净值日期": 1, "累计净值  (元)": 1, "资产净值  (元)": 1, "实收资本  (元)": 1, }))
        df['净值日期'] = pd.to_datetime(df['净值日期'])
        df.sort_values('净值日期', inplace=True)
        df['chg'] = df['累计净值  (元)'].pct_change()
        df.dropna(inplace=True)
        df['year'] = df['净值日期'].dt.year
        return df

    def get_dates_bench_chg(self, date_s='2022-01-01', date_e='2022-12-31'):
        """拉取基准收益率，为可视化超额展示提供数据"""
        df = pd.DataFrame(self.db_basic['w_bench_close'].find(
            {"date": {'$gte': date_s, '$lte': date_e}}, {"_id": 0, }, batch_size=1000000))

        df['沪深300'] = df['000300.SH'] / df.iloc[0]["000300.SH"] - 1
        df['中证500'] = df['000905.SH'] / df.iloc[0]["000905.SH"] - 1

        df_res = df[['date', '沪深300', '中证500']].copy()
        return df_res

    def get_dates_chg(self, date_s='2022-01-01', date_e='2022-12-31'):
        """拉取指定日期范围类的全A股票涨跌幅数据"""
        df_chg = pd.DataFrame(self.db_basic['w_stocks_chg'].find(
            {"date": {'$gte': date_s, '$lte': date_e}}, {"_id": 0, }, batch_size=1000000))
        df_chg = trans_str_to_float64(df_chg, trans_cols=['chg', ])
        df_chg.set_index(['date', 'code'], inplace=True)
        df_chg.sort_index(inplace=True)
        self.tmp_dates_chg_df = df_chg
        return df_chg

    def get_layer_factor(self, factor=None, date_s='2022-01-01', date_e='2022-12-31'):
        """分层回测单调性"""
        df_factor = self.__get_the_factor(factor, date_s=date_s, date_e=date_e)
        df_factor.set_index(['date', 'code'], inplace=True)
        df_factor.sort_index(inplace=True)
        return df_factor

    def get_group_by_cap_chg(self, date_s=None, date_e=None):
        if self.the_date is None:
            self.get_the_date()
        if date_s is None or date_e is None:
            df = pd.DataFrame(self.db_basic['w_stocks_daily'].find(
                {'date': self.the_date, 'paused': 0},
                {"_id": 0, 'date': 1, "code": 1, "market_cap": 1, 'chg': 1}))
        else:
            df = pd.DataFrame(self.db_basic['w_stocks_daily'].find(
                {'date': {'$gte': date_s, '$lte': date_e}, 'paused': 0},
                {"_id": 0, 'date': 1, "code": 1, "market_cap": 1, 'chg': 1}))
        return df

    def get_jq_today(self):
        today = datetime.date.today()
        jq.auth('17301739834', 'Shdq2021Shdq2021')
        print("今天还有 {} 数据查询量".format(jq.get_query_count()['spare']))
        trades = jq.get_trade_days(count=1).tolist()  # 返回截至到今日的前面交易日期（含今日）
        if today not in trades:
            raise Exception("今天 {} 不是交易日，不用运行！！")
        if datetime.datetime.now().hour < 15:
            raise Exception("还没收盘呢，不能运行！！")
        df_all_stock = jq.get_all_securities(date=today)  # 获取该天所有股票数据，返回DataFrame
        code_list = df_all_stock.index.tolist()
        columns = ['close', 'pre_close']

        df_today = jq.get_price(code_list, fields=columns, count=1, end_date=today, panel=False, frequency='1d',
                                skip_paused=True)
        df_today['chg'] = df_today.close / df_today.pre_close - 1
        df_today['code'] = df_today.code.map(lambda x: 'SH' + x[:6] if x.startswith('6') else 'SZ' + x[:6])
        df_today.insert(0, 'date', str(today))
        jq.logout()
        return df_today
