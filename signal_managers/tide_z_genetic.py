
from klines_managers import klines_ccxt
from signal_managers import indicators
from performance_analytics import metrics
from performance_analytics import backtest_plot
from backtesters import backtest


def make_tp_position_dict(lookback, qtl):
    tp_position_dict = {}
    for tp in ["TP1","TP2","TP3"]:
            tp_position_dict[tp] = {}
            for direction in ["long","short"]:
                    tp_position_dict[tp][direction] = {}
                    tp_position_dict[tp][direction]["lookback"] = lookback
                    tp_position_dict[tp][direction]["qtl"] = qtl
    return tp_position_dict



def init_tp_position_parameter_population():
        tp_position_dict = {}

        tp_position_list = []
        lookbacks = [3,6,9]
        qtls = [0.3, 0.6, 0.99]

        for lookback in lookbacks:
                for qtl in qtls:
                        tp_position_list.append(make_tp_position_dict(lookback, qtl))

        return tp_position_list

# =======================
# Load 1h klines
# =======================
import time
import pandas as pd
from klines_managers import klines_ccxt
from signal_managers.resampler import calc_klines_resample

from utils.list_type_converter import convert_to_type,convert_to_array
from signal_managers.indicators import calc_mfi_sig, param_func_mfi_EMAVol, param_func_mfi, calc_signal_TPSL
from signal_managers.indicators import calc_tide_sig, calc_tide_sig, param_func_tide_EMAVol, param_func_tide
from signal_managers.indicators import calc_z_sig, param_func_Z_EMAVol, param_func_Z
from signal_managers.composite_signals import merge_sig_dicts

from signal_managers.mfi_tide_z_signals import load_klines
from signal_managers.mfi_tide_z_signals import resample_instruments_dict
from signal_managers.mfi_tide_z_signals import calc_mfi_tide_z_signals

def initialise_parent(df=None,
                      instruments =  [
                                        "ccxt_kucoin__BTC-USDT",
                                        "ccxt_kucoin__ETH-USDT",
                                        "ccxt_currencycom__US500",
                                        "ccxt_currencycom__DXY",
                                        "ccxt_currencycom__Gold",
                                        "ccxt_currencycom__Oil - Crude",
                                        "ccxt_currencycom__NVDA",
                                        "ccxt_currencycom__UVXY"
                                        ],
                      timeframes = ["1h"],
                      timeframes_to_resample_to = ["2h","3h","4h","6h","8h","12h"],
                      instrument_to_trade = "ccxt_kucoin__BTC-USDT",
                      timeframe_to_trade = "1h",
                      signal_function = "z_sig",
                      signals_to_trade = "sig",
                      backtest_window = ["2021-01-01","2023-12-31"],
                      sig_lag=0,
                      kline_to_trade = f"close",
                      volume_to_trade= f"volume",
                      fee = 0.001,
                      slippage = 0.0,
                      min_holding_period = 23,
                      max_holding_period = 1e6,
                      long_equity = 5e5,
                      long_notional=5e5,
                      short_equity = 5e5,
                      short_notional= 5e5,
                      show_plots=True, 
                      figsize = (20,15), 
                      chosen_to_debug = None
                      ):

    instruments_dict = load_klines(instruments = instruments, timeframes=timeframes)
        
         
    instruments_dict = resample_instruments_dict(instruments_dict,
                                             resample_to_list = timeframes_to_resample_to,
                                             first_timeframe = timeframe_to_trade)

    sig_dicts = calc_mfi_tide_z_signals(instruments_dict,chosen_to_debug=[])


    df_to_trade = merge_sig_dicts(sig_dicts, 
                        instrument_to_trade = instrument_to_trade,
                        timeframe_to_trade = timeframe_to_trade,
                        reduce_col_names = True)
    
    df_backtested, df_trades, df_summary = objective_function(df_to_trade,
                                                          backtest_window = ["2021-01-01","2023-12-31"],
                                                          instrument_to_trade = "ccxt_kucoin__BTC-USDT",
                                                          timeframe_to_trade = "1h",
                                                          signal_function = "z_sig",
                                                          signals_to_trade = "sig",
                                                          sig_lag=0,
                                                          kline_to_trade = f"close",
                                                          volume_to_trade= f"volume",
                                                          fee = 0.001,
                                                          slippage = 0.0,
                                                          min_holding_period = 23,
                                                          max_holding_period = 1e6,
                                                          long_equity = 5e5,
                                                          long_notional=5e5,
                                                          short_equity = 5e5,
                                                          short_notional= 5e5,
                                                          show_plots=True, 
                                                          figsize = (20,15), 
                                                          mutate_signals_w_TP = True,
                                                          tradable_times = None, #[["00:05", "23:50"]]
                                                          closing_session_times= None, #[["23:50", "00:00"]]
                                                          )
    

    


import numpy as np
import pandas as pd
from signal_managers.indicators import calc_tide_strengths

def find_max_sharpe(df):
    max_sharpe = df['sharpe'].max()
    max_sharpe_row = df.loc[df['sharpe'] == max_sharpe]
    return max_sharpe_row

def objective_function(df=None,
                      instruments =  [
                                        "ccxt_kucoin__BTC-USDT",
                                        "ccxt_kucoin__ETH-USDT",
                                        "ccxt_currencycom__US500",
                                        "ccxt_currencycom__DXY",
                                        "ccxt_currencycom__Gold",
                                        "ccxt_currencycom__Oil - Crude",
                                        "ccxt_currencycom__NVDA",
                                        "ccxt_currencycom__UVXY"
                                        ],
                      backtest_window = ["2021-01-01","2023-12-31"],
                      instrument_to_trade = "ccxt_kucoin__BTC-USDT",
                      timeframe_to_trade = "1h",
                      signal_function = "z_sig",
                      model_name= "Trend_Following",
                      signal_to_trade = "sig",
                      sig_lag=0,
                      kline_to_trade = f"close",
                      volume_to_trade= f"volume",
                      fee = 0.001,
                      slippage = 0.0,
                      min_holding_period = 23,
                      max_holding_period = 1e6,
                      long_equity = 5e5,
                      long_notional=5e5,
                      short_equity = 5e5,
                      short_notional= 5e5,
                      show_plots=True, 
                      figsize = (20,15), 
                      run_signals_w_TP= True,
                      mutate_signals_w_TP = True,
                      tradable_times = None, #[["00:05", "23:50"]]
                      closing_session_times= None, #[["23:50", "00:00"]]
                      debug_verbose=True,
                      **kwargs):

        # =======================
        # BACKTEST
        # =======================
        print(f"\n{'='*30}\n(1) Generate base {signal_to_trade}-signal to backtest so that can generate positions taken\n{'='*30}\n")


        title = f"{timeframe_to_trade} {instrument_to_trade} {signal_to_trade} | fees: {fee*1e4} bps"
        file_name = f"{timeframe_to_trade} {instrument_to_trade} Z"

        df_sig = df.copy()
        # df_sig["sig"] = df_sig[signals_to_trade]#.shift(-1).fillna(method="ffill")
        # df_trade = df_sig[backtest_window[0]:backtest_window[1]].copy()
        # signals_to_trade= ["sig",signals_to_trade]

        df_trade = df_sig[backtest_window[0]:backtest_window[1]].copy()
        # df_trade["sig"] = df_trade[signal_to_trade]#.shift(-1).fillna(method="ffill")
        signals_to_trade= list(df_trade.columns)
        df_backtested,df_trades,df_summary = backtest.backtest(model_name= model_name,
                                                        df0=df_trade,
                                                        timeframe=timeframe_to_trade,
                                                        kline_to_trade=kline_to_trade,
                                                        volume_to_trade = volume_to_trade,
                                                        tradable_times = tradable_times,
                                                        closing_session_times = closing_session_times,
                                                        position_sizing_to_trade=None,
                                                        min_holding_period=min_holding_period,#/int(timeframe[:-1]),
                                                        max_holding_period=max_holding_period,#/int(timeframe[:-1]),
                                                        sig_lag=sig_lag,
                                                        fee=fee,
                                                        slippage=slippage,
                                                        long_equity = long_equity,
                                                        short_equity = short_equity,
                                                        long_notional=long_notional,
                                                        short_notional=short_notional,
                                                        signals=signals_to_trade, 
                                                        signal_function=signal_function, 
                                                        figsize=figsize, # width, height
                                                        show_B=True,
                                                        show_LS=True,
                                                        title=title,
                                                        file_name=file_name,
                                                        plots=show_plots,
                                                        diagnostics_verbose=False,
                                                        trail_SL = None,
                                                        trail_TP = None,
                                                        trail_increment = None,
                                                        N=365*24,
                                                        **kwargs)

        if run_signals_w_TP: 
            print(f"\n{'='*30}\n(2) TP based {signal_to_trade} signal\n{'='*30}\n")
            title = f"{timeframe_to_trade} {instrument_to_trade} {signal_to_trade} TP | fees: {fee*1e4} bps"
            file_name = f"{timeframe_to_trade} {instrument_to_trade} {signal_to_trade} TP"
            dfmtzTP = indicators.calc_signal_TPSL(df_backtested, 
                            signal = signal_to_trade,
                            penalty = 1, # this widens the SL so that it is not hit too often
                            tp_position_dict =  {"TP1": {"L":{"lookback":6, "qtl": 0.1}, 
                                                    "S": {"lookback":6, "qtl":0.1}
                                                    },
                                            "TP2": {"L":{"lookback":9, "qtl": 0.5}, 
                                                    "S": {"lookback":9, "qtl":0.5}
                                                    },
                                            "TP3": {"L":{"lookback":12, "qtl": 0.6}, 
                                                    "S": {"lookback":12, "qtl":0.6}
                                                    }
                                            }
                            )

            # signal_function2=f"z_sig_TP"
            signal_function2 = f"{signal_to_trade}_TP"
            # Settings for long or short bias, since different trajectories with either

            # print(df_sig["sig"].hist())

            """
            This part here should be the same as the base strategy, but with the new TP overlays eg:
            - TP1_long hit but not TP1_long_t so even though z_signal has flipped, lets chill first
            - TP1_long hit and TP1_long_t hit so lets close the position
            - TP1_long hit and TP1_long_t not hit so lets close the position if risk reward is high
            """
            # df_sig["sig"] = df_sig[signals_to_trade]#.shift(-1).fillna(method="ffill")
            # print(dfmtzTP.filter(regex="sig_long_SL2")) there is sig_long_SL2 here 
            df_trade = dfmtzTP[backtest_window[0]:backtest_window[1]].copy()
            # df_trade["sig"] = df_trade[signals_to_trade]#.shift(-1).fillna(method="ffill")
            signals_to_trade= list(df_trade.columns)
            df_backtested,df_trades,df_summary = backtest.backtest(model_name= model_name,
                                                            df0=df_trade,
                                                            timeframe=timeframe_to_trade,
                                                            kline_to_trade=kline_to_trade,
                                                            volume_to_trade = volume_to_trade,
                                                            tradable_times = tradable_times,
                                                            closing_session_times = closing_session_times,
                                                            position_sizing_to_trade=None,
                                                            min_holding_period=min_holding_period,#/int(timeframe[:-1]),
                                                            max_holding_period=max_holding_period,#/int(timeframe[:-1]),
                                                            sig_lag=sig_lag,
                                                            fee=fee,
                                                            slippage=slippage,
                                                            long_equity = long_equity,
                                                            short_equity = short_equity,
                                                            long_notional=long_notional,
                                                            short_notional=short_notional,
                                                            signals=signals_to_trade, 
                                                            signal_function=signal_function2, 
                                                            figsize=figsize, # width, height
                                                            show_B=True,
                                                            show_LS=True,
                                                            title=title,
                                                            file_name=file_name,
                                                            plots=True,
                                                            diagnostics_verbose=False,
                                                            trail_SL = None,
                                                            trail_TP = None,
                                                            trail_increment = None,
                                                            N=365*24
                                                            )
        # =======================
        # Mutate new tide strategy
        # =======================
        # has to have muateted something necessary for survival or remove unnecessary traits
        # 1. mutate the tide by adding a new window
        # 2. mutate the TP by adding a new window
        # 3. mutate the SL by adding a new window

        if mutate_signals_w_TP and run_signals_w_TP:
                print(f"\n{'='*30}\n(3) MUTATING SIGNALS USING TP and run strat again\n{'='*30}\n")

                # 1st round of mutated backtest
                dfmtzTP = indicators.calc_signal_TPSL(df_backtested, 
                                signal = "sig",
                                penalty = 1, # this widens the SL so that it is not hit too often
                                tp_position_dict = {"TP1": {"long":{"lookback":6, "qtl": 0.1}, 
                                                        "short": {"lookback":6, "qtl":0.1}
                                                        },
                                                "TP2": {"long":{"lookback":9, "qtl": 0.2}, 
                                                        "short": {"lookback":9, "qtl":0.2}
                                                        },
                                                "TP3": {"long":{"lookback":12, "qtl": 0.3}, 
                                                        "short": {"lookback":12, "qtl":0.3}
                                                        }
                                                }
                                )
                dfmtzTP = mutate_signals(dfmtzTP,sig_to_mutate="sig")


                signal_function="z_sig_TP"
                # Settings for long or short bias, since different trajectories with either

                # print(df_sig["sig"].hist())
                # df_sig["sig"] = df_sig[signals_to_trade]#.shift(-1).fillna(method="ffill")
                df_trade = dfmtzTP[backtest_window[0]:backtest_window[1]].copy()
                # df_trade["sig"] = df_trade[signals_to_trade]#.shift(-1).fillna(method="ffill")
                signals_to_trade= list(df_trade.columns)
                title = f"{timeframe_to_trade} {instrument_to_trade} Z TP mutant| fees: {fee*1e4} bps"
                file_name = f"{timeframe_to_trade} {instrument_to_trade} Z TP mutant"
                df_backtested,df_trades,df_summary = backtest.backtest(model_name= model_name,
                                                                df0=df_trade,
                                                                timeframe=timeframe_to_trade,
                                                                kline_to_trade=kline_to_trade,
                                                                volume_to_trade = volume_to_trade,
                                                                tradable_times = tradable_times,
                                                                closing_session_times = closing_session_times,
                                                                position_sizing_to_trade=None,
                                                                min_holding_period=min_holding_period,#/int(timeframe[:-1]),
                                                                max_holding_period=max_holding_period,#/int(timeframe[:-1]),
                                                                sig_lag=sig_lag,
                                                                fee=fee,
                                                                slippage=slippage,
                                                                long_equity = long_equity,
                                                                short_equity = short_equity,
                                                                long_notional=long_notional,
                                                                short_notional=short_notional,
                                                                signals=signals_to_trade, 
                                                                signal_function=signal_function, 
                                                                figsize=figsize, # width, height
                                                                show_B=True,
                                                                show_LS=True,
                                                                title=title,
                                                                file_name=file_name,
                                                                plots=show_plots,
                                                                diagnostics_verbose=False,
                                                                trail_SL = None,
                                                                trail_TP = None,
                                                                trail_increment = None,
                                                                N=365*24
                                                                )
                
                # START OUTPUT PRINTS =============================================================================================
                if False:
                        df = df_backtested.copy()
                        cols_to_seek = ["L_id","sig","L_positions","L_entry_price","L_exit_price", "S_positions","S_entry_price","S_exit_price"]
                        L_id_to_seek = df["L_id"].iloc[20:40].min() #df["L_id"].dropna().iloc[-1]
                        print(f"{'===='*20}\nAFTER Mutated backtest\n{'===='*20}\n-->\n{L_id_to_seek}")
                        df_to_print = df[df["L_id"] == L_id_to_seek][cols_to_seek]
                        print(df_to_print.head(3))
                        print(df_to_print.tail(3))
                        df_to_print = df_backtested[df_backtested["L_id"]==L_id_to_seek][cols_to_seek]
                        print(df_to_print.head(2))
                        print(df_to_print.tail(2))
                # END PRINTS ======================================================================================================

                
 
        return df_backtested, df_trades, df_summary

def mutate_signals(df,sig_to_mutate, debug_verbose = True):
    sig = sig_to_mutate

    # START OUTPUT PRINTS ============================================================================================
    if False:
        cols_to_seek = ["L_id","sig","L_positions","L_entry_price","L_exit_price", "S_positions","S_entry_price","S_exit_price"]
        L_id_to_seek = df["L_id"].iloc[20:40].min() #df["L_id"].dropna().iloc[-1]  
        print(f"{'===='*20}\nBEFORE SIGNAL MUTATION\n{'===='*20}\n-->\n{df['L_id'].dropna().iloc[-1]}")
        df_to_print = df[df["L_id"]==L_id_to_seek][cols_to_seek]
        print(df_to_print.head(3))
        print(df_to_print.tail(3))
    # END PRINTS ======================================================================================================

    # TP signal mutation
    # L_TP_signal_concur = all(df["L_positions"].values>0)
    # S_TP_signal_concur = all(df["S_positions"].values<0)
    L_TP_signal_concur = np.where(df["L_positions"]>0,True,False)
    S_TP_signal_concur = np.where(df["S_positions"]<0,True,False)
    # print(df[sig].values>0)
    # L_sig_concur = all(df[sig].values >0)
    # S_sig_concur = all(df[sig].values >0)
    L_sig_concur = np.where(df[sig]>2,True,False)
    S_sig_concur = np.where(df[sig]<-2,True,False)
    # print(f"L_TP_signal_concur: {L_TP_signal_concur[20:40]} ||| L_sig_concur: {L_sig_concur[20:40]}")
#     print(f"L_TP_signal_concur: {np.shape(L_TP_signal_concur)} ||| L_sig_concur: {np.shape(L_sig_concur)} || len(df): {len(df)}")
#     print(f"df: {np.shape(df)}")
    # print(f"!!!!!!!!!!!!!!!!!!!!!! why is open 30? ---> {sig}")
    df[sig] = np.where(S_TP_signal_concur & S_sig_concur,-2,0) + np.where(L_TP_signal_concur | L_sig_concur,2,0)
#     df[sig[0]] = np.where(L_TP_signal_concur & L_sig_concur,2,-2)
    # START OUTPUT PRINTS =============================================================================================
    if False:
        L_id_to_seek = df["L_id"].iloc[20:40].min()
        print(f"{'===='*20}\nAFTER SIGNAL MUTATION\n{'===='*20}\n-->\n{L_id_to_seek}")
        df_to_print = df[df["L_id"]==L_id_to_seek][cols_to_seek]
        print(df_to_print.head(3))
        print(df_to_print.tail(3))
    # END PRINTS ======================================================================================================

    return df

def evaluate_population(df, parameters, generations=6,signal_function="strengths", window =["2020-01-01","2022-12-31"], plot=True, verbose=True):
    sharpe_results = {}
    for i in range(generations):
        df, df_summary = evaluate(df,
                                  parameters['sensitivity'],
                                  parameters['threshold'],
                                  parameters['windows'],
                                  parameters['TPs'],
                                  parameters['SL_penalty'],
                                  signal_function=signal_function,
                                  window =window,
                                  plot = False,
                                )
        sharpe_results.update({i:{'sharpe':df_summary.iloc[0,0], 'df':df, 'df_summary':df_summary,'parameters':parameters}})
        if verbose: print(f"Sharpe: {df_summary.iloc[0,0]} | Sensitivity: {parameters['sensitivity']} | Thresholds: {parameters['threshold']} | Windows: {parameters['windows']} | TP: {parameters['TPs']} | SL: {parameters['SL_penalty']}")


    df = pd.DataFrame(sharpe_results).T
    if plot:
        df.plot(title=f"sensitivity: {parameters['sensitivity']}, window: {parameters['windows']}, threshold: {parameters['threshold']}", xlabel="generations", ylabel="sharpe ratio")
    max_sharpe_row = find_max_sharpe(df)
    best_df = max_sharpe_row['df'].values[0]
    best_df_summary = max_sharpe_row['df_summary'].values[0]
    best_parameters = max_sharpe_row['parameters'].values[0]
    return df, best_df,best_df_summary, best_parameters, max_sharpe_row
