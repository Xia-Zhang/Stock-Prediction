#!/usr/bin/python
# -*- coding: utf-8 -*-
from snownlp import SnowNLP

# 文件每行格式：[url + "\t" + date + "\t" + category + "\t" + title + "\t" + 对齐的股票代码 + "\t" + 新闻正文内容文本]。与数据集(2)对应相同股票
def get_sentiments(from_date, to_date):
    s = SnowNLP(u'''1、中信证券在经纪、投行业务市场份额中均处于行业领先地位,为新业务的扩张提供了优质的客户和渠道基础;
        2、对经纪业务依赖度较低,在差异化转型中已经具有先发优势;
        3、净资本规模、风控水平和综合能力使其成为新业务试点的首选券商,将长期享受“优先布局”的去监管政策红利。
        去监管政策逐项落地将使行业估值底部逐步抬升。
        自下而上创新过程中,证券公司在支付、托管、交易等基础功能领域正逐步扩展。
        去监管政策阶段性推出、逐步验证利润的过程将使行业估值底部在震荡中逐步抬升''')
    for sub in s.summary(5):
        print sub

    s = SnowNLP(u'中信证券:12年净利润同比下滑66.2%    600030  中信证券(600030.CH/人民币13.85;6030.HK/港币20.40,持有)昨日发布业绩快报,2012年实现归属于上市公司股东的净利润42.55亿元,同比下滑66.2%。 我们对此评论如下: 1)中信证券利润同比大幅下滑的主要原因,是由于公司在2011年出售华夏基金51%的股权而实现约131亿元的投资收益,如果剔除这部分一次性收益的影响,我们估计中信证券2012年净利润同比正增长50%左右,在艰难的市场环境下能实现这样的业绩已属不易。中信证券前三季度净利润同比下滑12.4%,能在4季度实现业绩反转,我们估计主要是得益于有效的人员费用控制,12月份A股市场的强劲反弹以及金石投资等子公司的良好表现。 2)2012年A股市场总体表现不佳,两市股票成交量同比下滑29.4%,IPO融资金额下降63.4%。在不利的市场环境下,中信证券经营仍有亮点:其投资银行业务表现强劲,股权承销金额同比仅下降13%,债券承销金额则同比增长37%;融资融券业务发展迅速,年末余额达88亿元,市场份额9.9%,在各券商中排名第一。 3)目前中信证券A股股价相当于1.76倍2012年市净率或1.67倍2013年市净率,35.84倍2012年市盈率或24.89倍2013年市盈率;H股股价相当于2.09倍2012年市净率或1.97倍2013年市净率,42.49倍2012年市盈率或29.51倍2013年市盈率。我们预测中信证券2013年净利润同比增速将在44%,但其ROE仅能从2012年的4.92%上升至6.88%,估值相比ROE仍然偏高。我们认为券商股的投资价值主要在于大盘反弹时的高弹性,因此短期策略仍以把握交易性机会为主。维持对中信证券A股和H股的持有评级不变。')
    for sub in s.summary(5):
        print(sub)
        print SnowNLP(sub).sentiments

if __name__ == '__main__':
    print(get_sentiments(1, 2))