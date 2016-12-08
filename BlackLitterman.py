# -*- coding: utf-8 -*-
"""
Created on Sat Nov  5 17:42:53 2016

@author: Hugo Fallourd, Dakota Wixom, Yun Chen, Sanket Sojitra, Sanjana Cheerla, Wanting Mao, Chay Pimmanrojnagool, Teng Fei

"""
import numpy as np
from scipy import linalg

# blacklitterman
#   This function performs the Black-Litterman blending of the prior
#   and the views into a new posterior estimate of the returns using the
#   alternate reference model as shown in Idzorek's paper.
# Inputs
#   delta  - Risk tolerance from the equilibrium portfolio
#   weq    - Weights of the assets in the equilibrium portfolio
#   sigma  - Prior covariance matrix
#   tau    - Coefficiet of uncertainty in the prior estimate of the mean (pi)
#   P      - Pick matrix for the view(s)
#   Q      - Vector of view returns
#   Omega  - Matrix of variance of the views (diagonal)
# Outputs
#   Er     - Posterior estimate of the mean returns
#   w      - Unconstrained weights computed given the Posterior estimates
#            of the mean and covariance of returns.
#   lambda - A measure of the impact of each view on the posterior estimates.
#
def altblacklitterman(delta, weq, sigma, tau, P, Q, Omega):
  # Reverse optimize and back out the equilibrium returns
  # This is formula (12) page 6.
  pi = weq.dot(sigma * delta)
  # We use tau * sigma many places so just compute it once
  ts = tau * sigma
  # Compute posterior estimate of the mean
  # This is a simplified version of formula (8) on page 4.
  middle = linalg.inv(np.dot(np.dot(P,ts),P.T) + Omega)
  er = np.expand_dims(pi,axis=0).T + np.dot(np.dot(np.dot(ts,P.T),middle),(Q - np.expand_dims(np.dot(P,pi.T),axis=1)))
  # Compute posterior estimate of the uncertainty in the mean
  # This is a simplified and combined version of formulas (9) and (15)
  # Compute posterior weights based on uncertainty in mean
  w = er.T.dot(linalg.inv(delta * sigma)).T
  # Compute lambda value
  # We solve for lambda from formula (17) page 7, rather than formula (18)
  # just because it is less to type, and we've already computed w*.
  lmbda = np.dot(linalg.pinv(P).T,(w.T * (1 + tau) - weq).T)
  return [er, w, lmbda]

# idz_omega
#   This function computes the Black-Litterman parameters Omega from
#   an Idzorek confidence.
# Inputs
#   conf   - Idzorek confidence specified as a decimal (50% as 0.50)
#   P      - Pick matrix for the view
#   Sigma  - Prior covariance matrix
# Outputs
#   omega  - Black-Litterman uncertainty/confidence parameter
#
def bl_omega(conf, P, Sigma):
  alpha = (1 - conf) / conf
  omega = alpha * np.dot(np.dot(P,Sigma),P.T)
  return omega
