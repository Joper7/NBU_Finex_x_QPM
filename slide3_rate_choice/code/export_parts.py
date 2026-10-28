import pickle, sys, pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment
from docx import Document
from docx.shared import Pt
O = sys.argv[1]
D = pickle.load(open('rate_scen.pkl', 'rb')); RES, PR = D['RES'], D['PR']
for v in RES.values(): v.attrs = {}
K = (15.0, 16.0, 17.0); LAB = {15.0: 'Рішення 15 %', 16.0: 'Рішення 16 % (база)', 17.0: 'Рішення 17 %'}
f = lambda x, d=2: f'{x:.{d}f}'.replace('.', ',').replace('-', '−')
charts = [('1_Ставка', 'r', 'Облікова ставка, % (середня за квартал)', 2, ''),
          ('2_Інфляція', 'cpi_yoy', 'Інфляція ІСЦ, % р/р', 2, 'Виділено 2027Q4 і 2028Q3'),
          ('3_ВВП', 'gdp_yoy', 'Реальний ВВП, % р/р', 2, 'Виділено 2027Q4'),
          ('4_Курс', 'eur_uah', 'Курс гривні до євро, грн/EUR', 2, 'Виділено 2028Q3')]
rows = [('Середня ставка 2026Q4, %', 'r', '2026Q4', 2), ('Реальна ставка 2026Q4 (ex ante), %', 'rr', '2026Q4', 1),
        ('Інфляція ІСЦ 2027Q4, % р/р', 'cpi_yoy', '2027Q4', 2), ('Інфляція ІСЦ 2028Q3, % р/р', 'cpi_yoy', '2028Q3', 2),
        ('ВВП 2027Q4, % р/р', 'gdp_yoy', '2027Q4', 2), ('Курс 2028Q3, грн/EUR', 'eur_uah', '2028Q3', 2),
        ('Резерви 2028Q3, міс. імпорту', 'MI', '2028Q3', 2), ('Імовірність утримати резерви ≥ 3 міс. імпорту в усі 8 кв., %', None, None, 1)]
fn = f'{O}/slide3_dani_dlia_hrafikiv.xlsx'
with pd.ExcelWriter(fn, engine='openpyxl') as w:
    for sh, v, t, d, note in charts:
        df = pd.DataFrame({LAB[k]: RES[k][v].round(d) for k in K}); df.index.name = 'Квартал'
        df.to_excel(w, sheet_name=sh, startrow=2)
        ws = w.sheets[sh]; ws['A1'] = t; ws['A1'].font = Font(bold=True, size=12); ws['A2'] = note
    tab = pd.DataFrame({LAB[k]: [round(100 * PR[k]['MI>=3 all8'], d) if v is None else round(float(RES[k].loc[q, v]), d) for _, v, q, d in rows] for k in K},
                       index=pd.Index([r[0] for r in rows], name='Показник'))
    tab.to_excel(w, sheet_name='5_Таблиця', startrow=2)
    w.sheets['5_Таблиця']['A1'] = 'Таблиця показників для слайду'; w.sheets['5_Таблиця']['A1'].font = Font(bold=True, size=12)
    for ws in w.sheets.values():
        ws.column_dimensions['A'].width = 58 if ws.title == '5_Таблиця' else 12
        for c in 'BCD': ws.column_dimensions[c].width = 20
        for row in ws.iter_rows(min_row=4):
            for c in row[1:]: c.number_format = '0.00'
    pal = pd.DataFrame({'Сценарій': [LAB[k] for k in K], 'Колір лінії (HEX)': ['#C8661A', '#008F99', '#5B3F8C'], 'Товщина': ['1,8 pt', '2,4 pt (виділена)', '1,8 pt']})
    pal.to_excel(w, sheet_name='6_Кольори', index=False); w.sheets['6_Кольори'].column_dimensions['A'].width = 24; w.sheets['6_Кольори'].column_dimensions['B'].width = 18

c15, c16, c17 = RES[15.0], RES[16.0], RES[17.0]
TXT = {
 'Заголовок': 'Чому 16 %, а не 15 % чи 17 %',
 'Підзаголовок': 'Три прогони FINEX-QPM на 8 кварталів',
 'Підпис під підзаголовком': 'рішення 29.10.2026 (чинність з 30.10): 15 %, 16 % або 17 %; далі ставка — за правилом (57)',
 'Ключове повідомлення (за бажанням)': f'Зміна рішення на ±1 п.п. змінює інфляцію лише на ∓0,2 п.п. і ВВП на ±0,07 п.п.; до 2027Q4 ставки всіх прогонів сходяться. 16 % — рекомендація правила (57) і компроміс між дезінфляцією, ВВП і курсом.',
 'Висновок — заголовок': 'Висновок: компроміс між дезінфляцією, ВВП і курсом',
 'Висновок — 15 %': f'Сповільнює дезінфляцію (ІСЦ +{f(c15.loc["2027Q4","cpi_yoy"]-c16.loc["2027Q4","cpi_yoy"],1)} п.п. у 2027Q4) за мізерного виграшу ВВП (+{f(c15.loc["2027Q4","gdp_yoy"]-c16.loc["2027Q4","gdp_yoy"])} п.п.); слабша гривня (+{f(c15.loc["2028Q3","eur_uah"]-c16.loc["2028Q3","eur_uah"])} грн/EUR) і менші резерви. Знижувати при ІСЦ 10 % і очікуваннях 12 % — ризик для довіри; у 2028 р. правило вимагатиме вищої ставки ({f(c15.loc["2028Q3","r"],1)} %).',
 'Висновок — 16 %': f'Збігається з правилом (57): {f(c16.loc["2026Q4","r"])} % ≈ 16 %. Реальна ставка {f(c16.loc["2026Q4","rr"],1)} % проти нейтральної {f(c16.loc["2026Q4","rr_bar"],1)} % достатня, щоб ІСЦ знизився з 10,0 % до {f(c16.loc["2028Q3","cpi_yoy"],1)} % без додаткових втрат ВВП.',
 'Висновок — 17 %': f'Інфляція нижча лише на {f(c16.loc["2027Q4","cpi_yoy"]-c17.loc["2027Q4","cpi_yoy"],1)} п.п., ціль 5 % на горизонті однаково не досягається; ВВП −{f(c16.loc["2027Q4","gdp_yoy"]-c17.loc["2027Q4","gdp_yoy"])} п.п., реальна ставка {f(c17.loc["2026Q4","rr"],1)} %. Ефект короткий: до 2027Q4 ставки всіх прогонів сходяться ({f(c15.loc["2027Q4","r"],1)}–{f(c17.loc["2027Q4","r"],1)} %).',
 'Примітка (методика)': '16 % — базовий прогноз (правило (57) дає середню 2026Q4 15,92 %). 15 % і 17 % — той самий прогноз + одноразовий шок правила (57) у 2026Q4: нова ставка діє 63 з 92 днів кварталу, тож середня 2026Q4 змінюється на ∓0,68 п.п.; з 2027Q1 ставка — за правилом. Імовірність — 5000 бутстреп-траєкторій шоків (без 2022 р.), центрованих на кожному прогоні; віяло резервів широке через історичні шоки офіційного фінансування.',
 'Джерело': 'Джерело: модель команди',
 'Колонтитул': 'Жовтень 2026',
}
doc = Document(); st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11)
doc.add_heading('Слайд після 2: тексти', level=1)
for k_, v_ in TXT.items():
    p = doc.add_paragraph(); r = p.add_run(k_); r.bold = True; r.font.size = Pt(9)
    doc.add_paragraph(v_)
doc.add_heading('Назви міні-графіків', level=2)
for _, _, t, _, note in charts: doc.add_paragraph(f'{t}' + (f' — {note}' if note else ''), style='List Bullet')
doc.add_paragraph('Легенда: «рішення 29.10: 15 %», «рішення 29.10: 16 % (база)», «рішення 29.10: 17 %».')
doc.add_heading('Таблиця показників', level=2)
t = doc.add_table(rows=1, cols=4); t.style = 'Table Grid'
for c, h in zip(t.rows[0].cells, ['Показник', '15 %', '16 %', '17 %']): c.text = h
for name, v, q, d in rows:
    cs = t.add_row().cells; cs[0].text = name
    for c, k in zip(cs[1:], K): c.text = f(100 * PR[k]['MI>=3 all8'] if v is None else RES[k].loc[q, v], d)
doc.save(f'{O}/slide3_teksty.docx')
with open(f'{O}/slide3_teksty.txt', 'w', encoding='utf-8') as fh:
    for k_, v_ in TXT.items(): fh.write(f'[{k_}]\n{v_}\n\n')
print('ok')
