from content_from_pdf import *


hedge_fund = [
    "hedge fund", 
    "Absolute Return", 
    "Accredited Investor", 
    "Alpha", 
    "Arbitrage", 
    "Attribution", 
    "Beta", 
    "Correlation", 
    "Drawdown", 
    "Hurdle Rate",
    "Leverage", 
    "Opportunistic",
    "Pairs Trading",
    "Portfolio Simulation",
    "Sharpe Ratio",
    "Short Rebate",
    "R-Squared",
    "Transportable Alpha",
    "Value at Risk"
    ]


private_equity = [
    "Private equity",
    "Angel investing",
    "Venture capital", 
    "Asset class", 
    "Asset allocation", 
    "Growth", 
    "Buyout",  
    "Leveraged buyout", 
    "LBO", 
    "Distressed", 
    "Turnaround", 
    "Asset-backed", 
    "Target", 
    "Sponsor", 
    "Independent Sponsor", 
    "Fundless Sponsor", 
    "Management", 
    "Current ownership", 
    "Anchor investor", 
    "Co-investor", 
    "Operating partners", 
    "Due Diligence", 
    "Teaser", 
    "Deal memo",
    "deal pack", 
    "Data room", 
    "deal room", 
    "QofE", 
    "Quality of Earnings", 
    "EBITDA", "Revenue",
    "Purchase multiple", 
    "Enterprise value", 
    "valuation", 
    'PE funds', 
    "Direct investing", 
    "Co-investing", 
    "LP co-investing",
    "Direct co-investing", 
    "Primary issuances", 
    "Secondary purchases", 
    "Minimum", 
    "Soft commitment", 
    "Hard commitment", 
    "Change of control", 
    "Liquidation event", 
    "Liquidity event", 
    "Dividend", 
    "Security", 
    "Gross returns", 
    "Net returns", 
    "Holding period", 
    "MOIC", "MOM", "IRR", 
    "Current yield", 
    "Carried interest", 
    "Promote", 
    "Performance-based fees", 
    "Hurdle rate", 
    "Preferred return", 
    "Waterfall", 
    "Sliding fee scale", 
    "Closing fee", 
    "Management fee", 
    "IOI", "LOI", "SPV", "NDA", 
    "Non-circ", "GP", "LP", 
    "Committed capital", 
    "Fund mandate", 
    "Capital call", 
    "Drawdown", 
    "Vintage year", 
    "J-curve"]


def check_doc_type(text_list):
    private = 0
    hedge = 0
    for word in private_equity:
        if word.lower() in text_list.lower():
            private += 1
    for word in hedge_fund:
        if word.lower() in text_list.lower():
            hedge += 1
    percentage_private = (private/(len(private_equity)))*100
    percentage_hedge = (hedge/(len(hedge_fund)))*100

    if percentage_hedge > percentage_private:
        return("Hedge Fund")
    elif percentage_private > percentage_hedge:
        return("Private Equity")


def checking_doc_type_result(filename):
    text_list = extractText(filename)
    text_list_refined = str(text_list[0]).replace('\n', ' ')
    result = check_doc_type(text_list_refined)
    return result
