# Utils module for Erdos's quant finance bootcamp
import numpy as np
from scipy.stats import norm


# Analytic pricers
# - Black-Scholes
def bs_price(S0, K, sigma, t, r, option_type='call'):
    '''
    Black-Scholes Call Option formula

    Inputs:
    S0 (float): Stock price at time 0
    K (float): Strike Price
    sigma (float): Yearly volatility
    t (float): Time to expiration (years)
    r (float): Risk-free Interest rate


    Return:
    Black-Scholes value of call/put option (float)
    '''

    d1 = (np.log(S0/K) + (r + (0.5)*sigma**2)*t)/(sigma*np.sqrt(t))
    d2 = d1 - sigma*np.sqrt(t)
    
    if option_type == 'put':
        return -S0*norm.cdf(-d1) + K*np.exp(-r*t)*norm.cdf(-d2)
    elif option_type == 'call':
        return S0*norm.cdf(d1) - K*np.exp(-r*t)*norm.cdf(d2)
    else:
        raise ValueError("Unrecognized option type: {}".format(option_type))


def bs_delta(S0, K, sigma, t, r, option_type='call'):
    '''Black-Scholes Delta of Call Option
    
    Inputs:
    S0 (float): Stock price at time 0
    K (float): Strike Price
    sigma (float): Yearly volatility
    t (float): Time to expiration (years)
    r (float): Risk-free Interest rate
    
    
    Return:
    Black-Scholes rate of change of call/put option with respect to S_0
    '''

    d1 = (np.log(S0/K) + (r + (0.5)*sigma**2)*t)/(sigma*np.sqrt(t))

    if option_type == 'put':
        return norm.cdf(d1) - 1
    elif option_type == 'call':
        return norm.cdf(d1)
    else:
        raise ValueError("Unrecognized option type: {}".format(option_type))

# - geometric Asian option
def gao_price(S0, K, sigma, t, r, option_type='call'):
    '''Geometric Asian option pricer
    Inputs:
    S0 (float): Stock price at time 0
    K (float): Strike Price
    sigma (float): Yearly volatility
    t (float): Time to expiration (years)
    r (float): Risk-free Interest rate

    Return:
    Computed value of a geometric Asian call/put option (float)
    '''
    b = (r - sigma**2 / 6) / 2
    d1 = np.sqrt(3)*(np.log(S0/K) + (b + sigma**2 / 6)*t) / (sigma * np.sqrt(t))
    d2 = d1 - sigma * np.sqrt(t/3)

    if option_type == 'put':
        return K * np.exp(-r*t) * norm.cdf(-d2) - S0 * np.exp((b-r)*t) * norm.cdf(-d1)
    elif option_type == 'call':
        return S0 * np.exp((b-r)*t) * norm.cdf(d1) - K * np.exp(-r*t) * norm.cdf(d2)
    else:
        raise ValueError("Unrecognized option type: {}".format(option_type))

# - geometric Asian option delta
def gao_delta(S0, K, sigma, t, r, option_type='call'):
    '''Geometric Asian option delta
    
    Inputs:
    S0 (float): Stock price at time 0
    K (float): Strike Price
    sigma (float): Yearly volatility
    t (float): Time to expiration (years)
    r (float): Risk-free Interest rate
    
    Return:
    Delta of a geometric Asian call/put option (float)
    '''
    b = (r - sigma**2 / 6) / 2
    d1 = np.sqrt(3)*(np.log(S0/K) + (b + sigma**2 / 6)*t) / (sigma * np.sqrt(t))

    if option_type == 'put':
        return np.exp((b-r)*t) * (norm.cdf(d1) - 1)
    elif option_type == 'call':
        return np.exp((b-r)*t) * norm.cdf(d1)
    else:
        raise ValueError("Unrecognized option type: {}".format(option_type))

# - conditional geometric Asian option delta
def gao_asian_conditional_delta(S_t, G_t, K, sigma, tau, r, T):
    """
    Conditional delta of a geometric Asian call option at time t,
    given current spot S_t, running geometric average G_t,
    and remaining time tau = T - t.
    
    Parameters
    ----------
    S_t : np.ndarray or float
        Current underlying price(s)
    G_t : np.ndarray or float
        Current running geometric average(s)
    K : float
        Strike
    sigma : float
        Volatility
    tau : float
        Remaining time to maturity
    r : float
        Risk-free rate
    T : float
        Total maturity
    
    Returns
    -------
    np.ndarray or float
        Conditional delta(s)
    """
    if tau <= 0:
        return np.where(G_t > K, 1.0, 0.0)

    # Effective parameters
    sigma_eff = sigma * np.sqrt(tau / (3 * T))
    r_eff = (tau / (2 * T)) * (r - 0.5 * sigma**2) + (sigma**2 * tau) / (6 * T)

    # Effective underlying
    S_eff = G_t * (S_t / G_t) ** (tau / T)

    # d1
    d1 = (np.log(S_eff / K) + r_eff + 0.5 * sigma_eff**2) / sigma_eff

    # Partial derivative of S_eff wrt S_t
    dS_eff_dS = (tau / T) * S_eff / S_t

    # Delta
    Delta = np.exp(-r * tau) * np.exp(r_eff + 0.5 * sigma_eff**2) * norm.cdf(d1) * dS_eff_dS

    return Delta



# Monte Carlo methods
# - stock paths generator
def GBM_paths(S0, sigma, t, r, mu, n_sims, n_steps):
    """Simulates stock paths as geometric Brownian Motions
    Inputs:
    S0 (float): Underlying stock price at time 0
    sigma (float): Yearly volatility
    t (float): Time to expiration (years)
    r (float): Risk-free interest rate
    mu (float): Drift of log-returns
    n_sims (int): Number of simulated paths
    n_steps (int): Number of steps in each simulated path, each step interval has length t/n_steps
    
    Return (np.array): Array of stock paths
    """
    
    noise = np.random.normal(loc = 0, scale = 1, size = (n_sims, n_steps))
    log_returns = (mu+r-sigma**2*(0.5))*t/n_steps + sigma*np.sqrt(t/n_steps)*noise
    paths_with_start = np.insert(S0*np.exp(np.cumsum(log_returns, axis = 1)), 0, S0, axis = 1)

    return paths_with_start

# - European options
def monte_carlo_european(S0, K, sigma, t, r, mu, n_sims, n_hedges, return_distribution=True, option_type='call'):
    """Monte-Carlo simulation of a European option value with GBM assumptions with delta hedging.

    Inputs:
    S0 (float): underlying stock price at time 0
    K (float): strike price
    sigma (float): yearly volatility
    t (float): time to expiration (years)
    r (float): risk-free interest rate
    mu (float): drift of log-returns
    n_sims (int): number of simulated paths
    n_hedges (int): number of delta-hedges
    
    Returns:
    If return_distribution is true, returns distribution of simulated call values with delta hedging;
      if false, returns the average payoff and standard deviation of call option with delta hedging

    To simulate the profit distribution of selling n_options number of call options for a premium, run
    n_options*(premium - bs_MC_call(S0, K, sigma, t, r, mu, n_sims, n_hedges) - tr_cost*n_hedges)
    
    """
    if n_hedges == 0:
        paths = GBM_paths(S0, sigma, t, r, mu, n_sims, n_steps=1)
        S_t = paths[:, -1]  # Terminal prices

        if option_type == 'call':
            discounted_payoff = np.exp(-r * t) * np.maximum(S_t - K, 0)
        elif option_type == 'put':
            discounted_payoff = np.exp(-r * t) * np.maximum(K - S_t, 0)
        else:
            raise ValueError("Unrecognized option type: {}".format(option_type))

        if return_distribution:
            return discounted_payoff
        else:
            return np.mean(discounted_payoff), np.std(discounted_payoff)/np.sqrt(n_sims)

    else:
        paths = GBM_paths(S0, sigma, t, r, mu, n_sims, n_hedges)
        S_t = paths[:, -1]  # Terminal prices

        if option_type == 'call':
            discounted_payoff = np.exp(-r * t) * np.maximum(S_t - K, 0)
        elif option_type == 'put':
            discounted_payoff = np.exp(-r * t) * np.maximum(K - S_t, 0)
        else:
            raise ValueError("Unrecognized option type: {}".format(option_type))

        times = np.linspace(0, t, n_hedges + 1)

        deltas = bs_delta(paths[:,0:n_hedges], K, sigma, (t-times)[0:n_hedges], r, option_type=option_type)

        stock_profits_discounted = (paths[:,1:n_hedges + 1] - \
                                    paths[:,0:n_hedges]*np.exp(r*t/n_hedges))*np.exp(-r*times[1:n_hedges+1])*deltas

        profit_with_hedging = discounted_payoff - np.sum(stock_profits_discounted, axis=1)

        if return_distribution:
            return profit_with_hedging
        else:
            return np.mean(profit_with_hedging), np.std(profit_with_hedging)/np.sqrt(n_sims)

# - self-financing hedged European options
def mc_eur_sf_hedged(S0, K, sigma, t, r, mu, premium, n_sims, n_steps, option_type="call"):
    """Market-maker's profits on a self-financing European option delta-hedging portfolio

    Inputs:
    S0 (float): Underlying stock price at time 0
    sigma (float): Yearly volatility
    t (float): Time to expiration (years)
    r (float): Risk-free interest rate
    mu (float): Drift of log-returns
    premium (float): Premium of selling one option
    n_sims (int): Number of simulated paths
    n_steps (int): Number of steps in the average

    Returns:
    Distribution of profits
    """
    dt = t / n_steps

    paths = GBM_paths(S0, sigma, t, r, mu, n_sims, n_steps)
    S = paths[:,-1]

    if option_type == "call":
        payoff = np.maximum(S - K, 0)
    elif option_type == "put":
        payoff = np.maximum(K - S, 0)
    else:
        raise ValueError("Unrecognized option type: {}".format(option_type))

    # initial delta and bond position
    Delta = bs_delta(S0, K, sigma, t, r, option_type=option_type)
    V = premium
    B = V - Delta * S0


    for i in range(n_steps):
        S_next = paths[:, i+1]

        # bond accrues interest
        B *= np.exp(r * dt)

        # portfolio value before rebalancing
        V = Delta * S_next + B

        # compute new delta
        tau = t - (i + 1) * dt
        new_Delta = bs_delta(S_next, K, sigma, tau, r, option_type=option_type)

        # adjust bond for rebalancing cost
        B = B - (new_Delta - Delta) * S_next

        # update delta
        Delta = new_Delta

    V = Delta * S_next + B
    
    return (V - payoff) * np.exp(-r*t)

# - Asian options
def monte_carlo_asian(S0, K, sigma, t, r, mu, n_sims, n_steps, geometric=False, return_distribution=True, option_type="call"):
    """Monte-Carlo simulation of a Asian option value with Black-Scholes assumptions

    Inputs:
    S0 (float): Underlying stock price at time 0
    sigma (float): Yearly volatility
    t (float): Time to expiration (years)
    r (float): Risk-free interest rate
    mu (float): Drift of log-returns
    n_sims (int): Number of simulated paths
    n_steps (int): Number of steps in the average

    Returns:
    If return_distribution is true, returns distribution of simulated values;
      if false, returns the average payoff of option
    """
    paths = GBM_paths(S0, sigma, t, r, mu, n_sims, n_steps)
    if geometric:
        S = np.exp(np.mean(np.log(paths), axis=1))  # geometric mean of prices
    else:
        S = np.mean(paths, axis=1)  # arithmetic mean of prices

    if option_type == "call":
        discounted_payoff = np.exp(-r * t) * np.maximum(S - K, 0)
    elif option_type == "put":
        discounted_payoff = np.exp(-r * t) * np.maximum(K - S, 0)
    else:
        raise ValueError("Unrecognized option type: {}".format(option_type))

    if return_distribution:
        return discounted_payoff
    else:
        return np.mean(discounted_payoff)

# - self-financing hedged Asian options
def mc_asian_sf_hedged(S0, K, sigma, t, r, mu, premium, n_sims, n_steps, geometric=False, option_type="call"):
    """Market-maker's profits on a self-financing Asian option delta-hedging portfolio

    Inputs:
    S0 (float): Underlying stock price at time 0
    sigma (float): Yearly volatility
    t (float): Time to expiration (years)
    r (float): Risk-free interest rate
    mu (float): Drift of log-returns
    premium (float): Premium of selling one option
    n_sims (int): Number of simulated paths
    n_steps (int): Number of steps in the average

    Returns:
    Distribution of profits
    """
    dt = t / n_steps

    paths = GBM_paths(S0, sigma, t, r, mu, n_sims, n_steps)

    if geometric:
        S = np.exp(np.mean(np.log(paths), axis=1))  # geometric mean of prices
    else:
        S = np.mean(paths, axis=1)  # arithmetic mean of prices

    if option_type == "call":
        payoff = np.maximum(S - K, 0)
    elif option_type == "put":
        payoff = np.maximum(K - S, 0)
    else:
        raise ValueError("Unrecognized option type: {}".format(option_type))

    # initial delta and bond position
    Delta = gao_delta(S0, K, sigma, t, r, option_type=option_type)
    V = premium
    B = V - Delta * S0

    # initial geometric average (for conditional delta computation)
    G = np.full(n_sims, S0)

    for i in range(n_steps):
        S_next = paths[:, i+1]

        # bond accrues interest
        B *= np.exp(r * dt)

        # portfolio value before rebalancing
        V = Delta * S_next + B

        # update geometric average
        G = np.exp(((i+1) * np.log(G) + np.log(S_next)) / (i+2))

        # compute new delta
        S_eff = G * ((S_next / G)**(1-(i+1)/n_steps))
        sigma_eff = sigma * np.sqrt((1-(i+1)/n_steps)/3)
        tau = t - (i + 1) * dt
        new_Delta = (1 - (i + 1)/n_steps) * (S_eff / S_next) * gao_delta(
            S_eff, K, sigma_eff, tau, r, option_type=option_type
        )

        # adjust bond for rebalancing cost
        B = B - (new_Delta - Delta) * S_next

        # update delta
        Delta = new_Delta

    V = Delta * S_next + B
    
    return (V - payoff) * np.exp(-r*t)