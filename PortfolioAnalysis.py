# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 15:13:50 2016

@author: Hugo Fallourd, Dakota Wixom, Yun Chen, Sanket Sojitra, Sanjana Cheerla, Wanting Mao, Chay Pimmanrojnagool, Teng Fei

"""
from scipy.stats import norm
import math
import numpy
import pyfolio as pf
from pyfolio.tears import (create_full_tear_sheet,
                           create_returns_tear_sheet,
                           create_position_tear_sheet,
                           create_txn_tear_sheet,
                           create_round_trip_tear_sheet,
                           create_interesting_times_tear_sheet,
                           create_bayesian_tear_sheet)
                           
class PortfolioAnalysis(object):
    def __init__(self, p, b, h):
        self.portfolio = p
        self.benchmark = b
        self.horizon = h
        
    def RunAnalysis(self):
        
        create_interesting_times_tear_sheet(self.portfolio,self.benchmark,return_fig=True)
        create_full_tear_sheet(self.portfolio, positions=None, transactions=None, market_data=None, benchmark_rets=self.benchmark, gross_lev=None, slippage=None, sector_mappings=None, bayesian=False, round_trips=False, hide_positions=False, cone_std=(1.0, 1.5, 2.0), bootstrap=False, unadjusted_returns=None, set_context=True)

        # Time horizon for scaling. horizon = 1 -> 1-day VAR/CVAR
        self.AllVAR(self.portfolio, self.horizon, "Portfolio")
        self.AllVAR(self.benchmark, self.horizon, "Benchmark")

    # Calculate n-day VAR
    def calcVar(self,rets, scale=1):
        mu = numpy.mean(rets)
        std = numpy.std(rets)
        valueAtRisk = norm.ppf(0.05, mu, std)
        return(round(100*valueAtRisk*math.sqrt(scale),2))
    
    # Calculate n-day VAR
    def CVAR(self,rets, scale=1):
        VAR = self.calcVar(rets, scale=1)/100
        CVAR = rets[rets <= VAR].mean()
        return(round(100*CVAR*math.sqrt(scale),2))
        
    def AllVAR(self,rets, scale=1, name="Portfolio"):
        print(name+": ", "\n\tVAR: ", self.calcVar(rets, self.horizon),"%", "\n\tCVAR: ",self.CVAR(rets, self.horizon))
