# --- три прогони: рішення 29.10.2026 (чинність з 30.10) 15 / 16 / 17 %; база = правило (57) = «16 %»
import pickle
DAYS_NEW, DAYS_Q = 63, 92                      # 30.10-31.12 з 92 днів 2026Q4
r_base_q4 = float(BASE['r'].iloc[0])
SC = {}
for D_ in (15.0, 16.0, 17.0):
    dlt = (D_ - 16.0) * DAYS_NEW / DAYS_Q      # відхил середньої ставки 2026Q4 від правила
    S_ = BASE.copy() if D_ == 16.0 else simulate(MODEL, exog={('r', Y0): (r_base_q4 + dlt, 'e_r')})
    S_['gdp_yoy'] = [100 * (np.exp(sum((hist_dy + S_['dy'].tolist())[i:i + 4]) / 400) - 1) for i in range(H)]
    S_['cpi_yoy'] = 100 * (np.exp(S_['pi4'] / 100) - 1)
    SC[D_] = S_
    print(D_, 'dlt', round(dlt, 3), 'e_r', S_.attrs.get('shocks', {}))
# варіант «±1 п.п. до середньої 2026Q4» (як у формулюванні завдання) - для чутливості
SC1 = {}
for D_ in (15.0, 17.0):
    S_ = simulate(MODEL, exog={('r', Y0): (r_base_q4 + (D_ - 16.0), 'e_r')})
    S_['gdp_yoy'] = [100 * (np.exp(sum((hist_dy + S_['dy'].tolist())[i:i + 4]) / 400) - 1) for i in range(H)]
    S_['cpi_yoy'] = 100 * (np.exp(S_['pi4'] / 100) - 1)
    SC1[D_] = S_
# віяло: ті самі 5000 бутстреп-траєкторій шоків (без 2022 р.), центровані на кожному прогоні (лінійна модель: прогін + (SIMX - BASE0))
DEV = SIMX - BASE0[VNAMES].values[None, :, :]
PR = {}
for D_, S_ in SC.items():
    sims = S_[VNAMES].values[None] + DEV
    MIs = sims[:, :, VI['MI']]; FXRs = sims[:, :, VI['FXR']]; pis = sims[:, :, VI['pi4']]
    lvl = EUR0 * np.exp(np.cumsum(sims[:, :, VI['ds_eur']], axis=1) / 400)
    PR[D_] = {'MI>=3 all8': (MIs.min(1) >= 3).mean(), 'MI>=3 2028Q3': (MIs[:, -1] >= 3).mean(), 'MI>=3 2027Q4': (MIs[:, 4] >= 3).mean(),
              'MI min med': np.median(MIs.min(1)), 'MI p10 2028Q3': np.percentile(MIs[:, -1], 10),
              'pi4<=log(1.07) 2027Q4': (pis[:, 4] <= 100*np.log(1.07)).mean(),
              'cpi P10 2028Q3': 100*(np.exp(np.percentile(pis[:, -1], 10)/100)-1), 'cpi P90 2028Q3': 100*(np.exp(np.percentile(pis[:, -1], 90)/100)-1),
              'eur P10': np.percentile(lvl[:, -1], 10), 'eur P90': np.percentile(lvl[:, -1], 90),
              'eur>60 2028Q3': (lvl[:, -1] > 60).mean()}
cols = ['rr', 'rr_bar', 'pie', 'r', 'cpi_yoy', 'pi4', 'gdp_yoy', 'dy', 'y_gap', 'eur_uah', 'ds_eur', 'gam', 'fa_o', 'FXI', 'FXR', 'MI', 'OFF']
lab = [qlabel(t) for t in BASE.index]
RES = {D_: S_[cols].set_axis(lab).copy() for D_, S_ in SC.items()}
RES1 = {D_: S_[cols].set_axis(lab).copy() for D_, S_ in SC1.items()}
pd.set_option('display.width', 250)
for D_ in SC: print('=====', D_); print(RES[D_].round(3).to_string())
for D_ in SC1: print('===== ±1 avg', D_); print(RES1[D_][['r','cpi_yoy','gdp_yoy','eur_uah','MI']].round(3).to_string())
print(pd.DataFrame(PR).round(4).to_string())
pickle.dump({'RES': RES, 'RES1': RES1, 'PR': PR, 'r_base_q4': r_base_q4, 'X0r': R_LAST, 'R_Q_AVG': R_Q_AVG,
             'hist': {'r': SM['r'].loc[2023.0:].set_axis([qlabel(t) for t in SM.loc[2023.0:].index]),
                      'pi4': SM['pi4'].loc[2023.0:].set_axis([qlabel(t) for t in SM.loc[2023.0:].index]),
                      'MI': SM['MI'].loc[2023.0:].set_axis([qlabel(t) for t in SM.loc[2023.0:].index]),
                      'eur': HIST['eur_uah'].loc[2023.0:].set_axis([qlabel(t) for t in HIST.loc[2023.0:].index])},
             'fan_sims': {D_: (SC[D_][VNAMES].values[None] + DEV)[:, :, [VI['MI'], VI['pi4'], VI['ds_eur'], VI['dy']]] for D_ in SC}},
            open('rate_scen.pkl', 'wb'))
