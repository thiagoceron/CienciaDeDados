import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import geopandas as gpd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LinearRegression, Ridge, Lasso, LogisticRegression
from sklearn.metrics import (classification_report, confusion_matrix, ConfusionMatrixDisplay,
                             r2_score, mean_squared_error, roc_curve, auc, precision_recall_curve)
from scipy import stats
import ssl, urllib.request, json
import warnings
warnings.filterwarnings('ignore')


# PREPARAÇÃO DOS DADOS (para todos os modelos)
df = pd.read_csv('mamografia.csv')

periodos     = sorted(df['co_anomes'].unique())
anos_feature = periodos[:-1]
ano_target   = periodos[-1]

pivot = df.pivot_table(index='co_ibge', columns='co_anomes',
                       values='vl_indicador_calculado_mun', aggfunc='first').dropna()

regiao_map = df.drop_duplicates('co_ibge').set_index('co_ibge')['no_regiao_brasil']

media_nacional_2025 = df[df['co_anomes'] == ano_target]['vl_indicador_calculado_mun'].mean()

# Features base: histórico 2016-2024
X_base = pivot[anos_feature].copy()
X_base.columns = [f'ano_{c}' for c in X_base.columns]

# Features com dummies de região
X_base['regiao'] = X_base.index.map(regiao_map)
X_full = pd.get_dummies(X_base, columns=['regiao'], drop_first=True, dtype=float)

# Target binário
y_bin = (pivot[ano_target] >= media_nacional_2025).map(
    {True: 'Acima da média', False: 'Abaixo da média'}
)

# Target numérico para regressão
y_num = pivot[ano_target]

print("=" * 60)
print("  TRABALHO FINAL — CIÊNCIA DE DADOS")
print("  Dataset: Mamografia por Município (DATASUS)")
print("=" * 60)
print(f"\nMunicípios: {X_base.shape[0]} | Features: {X_base.shape[1]-1} anos + região")
print(f"Média nacional 2025: {media_nacional_2025:.1f} exames/município")
print(f"\nDistribuição das classes:")
for cls, cnt in y_bin.value_counts().items():
    print(f"   {cls:20s}: {cnt:4d} municípios ({cnt/len(y_bin)*100:.1f}%)")


# 1 kNN
print("\n" + "=" * 60)
print("  MODELO 1: k-Nearest Neighbors (kNN)")
print("=" * 60)

X_knn = pivot[anos_feature].copy()
X_knn.columns = [f'ano_{c}' for c in X_knn.columns]

X_train_k, X_test_k, y_train_k, y_test_k = train_test_split(
    X_knn, y_bin, test_size=0.30, random_state=42, stratify=y_bin
)

scaler_k    = StandardScaler()
Xtr_k       = scaler_k.fit_transform(X_train_k)
Xte_k       = scaler_k.transform(X_test_k)

k_values        = range(1, 16, 2)
weights_options = ['uniform', 'distance']
results_k       = []

print(f"\n{'k':>3} | {'weights':>8} | {'CV Mean Acc':>11} | {'CV Std':>7}")
print("─" * 45)
for w in weights_options:
    for k in k_values:
        knn = KNeighborsClassifier(n_neighbors=k, weights=w)
        cv  = cross_val_score(knn, Xtr_k, y_train_k, cv=5, scoring='accuracy')
        results_k.append({'k': k, 'weights': w, 'cv_mean': cv.mean(), 'cv_std': cv.std()})
        print(f"{k:>3} | {w:>8} | {cv.mean():>10.4f} | {cv.std():>7.4f}")

res_k_df     = pd.DataFrame(results_k)
best_k_row   = res_k_df.loc[res_k_df['cv_mean'].idxmax()]
best_k       = int(best_k_row['k'])
best_kw      = best_k_row['weights']

best_knn = KNeighborsClassifier(n_neighbors=best_k, weights=best_kw)
best_knn.fit(Xtr_k, y_train_k)
y_pred_k  = best_knn.predict(Xte_k)
acc_k     = best_knn.score(Xte_k, y_test_k)

print(f"\nMelhor configuração: k={best_k}, weights='{best_kw}'")
print(f"Acurácia CV média  : {best_k_row['cv_mean']:.4f}")
print(f"Acurácia no teste  : {acc_k:.4f}")
print(f"\nRelatório detalhado:")
print(classification_report(y_test_k, y_pred_k))

# Previsão de todos os municípios para o mapa
X_all_k    = scaler_k.transform(X_knn)
y_all_pred = best_knn.predict(X_all_k)
pred_df    = pd.DataFrame({'co_ibge': pivot.index.astype(str).str[:6], 'classe': y_all_pred})

# Carregar geojsons
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode    = ssl.CERT_NONE

url_mun = "https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-100-mun.json"
with urllib.request.urlopen(url_mun, context=ctx) as r:
    data = json.loads(r.read())
with open('/tmp/brazil_municipios.geojson', 'w') as f:
    json.dump(data, f)

url_states = "https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/brazil-states.geojson"
with urllib.request.urlopen(url_states, context=ctx) as r:
    states_data = json.loads(r.read())
with open('/tmp/brazil_states.geojson', 'w') as f:
    json.dump(states_data, f)

gdf        = gpd.read_file('/tmp/brazil_municipios.geojson')
states_gdf = gpd.read_file('/tmp/brazil_states.geojson')
gdf['id']  = gdf['id'].astype(str).str[:6]
gdf_merged = gdf.merge(pred_df, left_on='id', right_on='co_ibge', how='left')

# Gráficos kNN
ck = {'uniform': '#2196F3', 'distance': '#F44336'}
fig, axes = plt.subplots(2, 3, figsize=(20, 12))
fig.suptitle("kNN — Mamografia: Prever se município ficará acima da média nacional (2025)",
             fontsize=13, fontweight='bold')

ax = axes[0, 0]
for w in weights_options:
    sub = res_k_df[res_k_df['weights'] == w]
    ax.plot(sub['k'], sub['cv_mean'], marker='o', color=ck[w], label=f"weights='{w}'", linewidth=2)
    ax.fill_between(sub['k'], sub['cv_mean']-sub['cv_std'], sub['cv_mean']+sub['cv_std'], alpha=0.15, color=ck[w])
ax.axvline(best_k, color='green', linestyle='--', alpha=0.7, label=f'Melhor k={best_k}')
ax.set_xlabel('Valor de k'); ax.set_ylabel('Acurácia CV Média')
ax.set_title('Acurácia por k e Ponderação (CV=5)')
ax.legend(); ax.grid(True, alpha=0.3); ax.set_xticks(list(k_values))

ax = axes[0, 1]
for w in weights_options:
    sub = res_k_df[res_k_df['weights'] == w]
    ax.plot(sub['k'], sub['cv_std'], marker='s', color=ck[w], label=f"weights='{w}'", linewidth=2, linestyle='--')
ax.axvline(best_k, color='green', linestyle='--', alpha=0.7, label=f'Melhor k={best_k}')
ax.set_xlabel('Valor de k'); ax.set_ylabel('Desvio Padrão (CV)')
ax.set_title('Estabilidade do Modelo por k')
ax.legend(); ax.grid(True, alpha=0.3); ax.set_xticks(list(k_values))

ax = axes[0, 2]
cm = confusion_matrix(y_test_k, y_pred_k, labels=best_knn.classes_)
ConfusionMatrixDisplay(cm, display_labels=best_knn.classes_).plot(ax=ax, colorbar=False, cmap='Blues')
ax.set_title(f'Matriz de Confusão\n(k={best_k}, weights={best_kw})')

ax = axes[1, 0]
X_plot = X_knn.copy(); X_plot['target'] = y_bin.values; X_plot['exames_2024'] = pivot[anos_feature[-1]].values
for cls, cor in zip(['Acima da média', 'Abaixo da média'], ['#4CAF50', '#FF5722']):
    vals = X_plot[X_plot['target'] == cls]['exames_2024']
    ax.hist(vals[vals < vals.quantile(0.99)], bins=40, alpha=0.6, label=cls, color=cor)
ax.axvline(media_nacional_2025, color='black', linestyle='--', label=f'Média ({media_nacional_2025:.0f})')
ax.set_xlabel('Exames (2024)'); ax.set_ylabel('Nº municípios')
ax.set_title('Distribuição por Classe (2024)'); ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

ax = axes[1, 1]
x_pos = np.arange(len(list(k_values))); width = 0.35
u_v = res_k_df[res_k_df['weights']=='uniform'].set_index('k')['cv_mean']
d_v = res_k_df[res_k_df['weights']=='distance'].set_index('k')['cv_mean']
ax.bar(x_pos-width/2, u_v.values, width, label='uniform',  color='#2196F3', alpha=0.8)
ax.bar(x_pos+width/2, d_v.values, width, label='distance', color='#F44336', alpha=0.8)
ax.axhline(acc_k, color='green', linestyle=':', linewidth=2, label=f'Acc. Teste ({acc_k:.3f})')
ax.set_xlabel('Valor de k'); ax.set_ylabel('Acurácia CV Média'); ax.set_title('Uniforme vs Distance')
ax.set_xticks(x_pos); ax.set_xticklabels([str(k) for k in k_values])
ax.legend(fontsize=8); ax.grid(True, alpha=0.3, axis='y'); ax.set_ylim(0, 1.05)

ax = axes[1, 2]
color_map = {'Acima da média': '#4CAF50', 'Abaixo da média': '#FF5722'}
gdf_merged['color'] = gdf_merged['classe'].map(color_map).fillna('#CCCCCC')
gdf_merged.plot(ax=ax, color=gdf_merged['color'], edgecolor='none', linewidth=0)
states_gdf.plot(ax=ax, color='none', edgecolor='black', linewidth=0.5)
ax.legend(handles=[mpatches.Patch(color='#4CAF50', label='Acima da média'),
                   mpatches.Patch(color='#FF5722', label='Abaixo da média')], loc='lower left', fontsize=8)
ax.set_title(f'Previsão kNN por Município\n(k={best_k}, média = {media_nacional_2025:.0f})'); ax.set_axis_off()

plt.tight_layout()
plt.savefig('grafico_knn.png', dpi=150, bbox_inches='tight')
plt.show()
print("Gráfico kNN salvo!")


# 2 REGRESSÃO LINEAR SIMPLES
print("\n" + "=" * 60)
print("  MODELO 2: Regressão Linear Simples")
print("=" * 60)

x_rl = pivot[202312].values
y_rl = pivot[202412].values
mask_rl = (x_rl < np.percentile(x_rl, 99)) & (y_rl < np.percentile(y_rl, 99))
X_rl = x_rl[mask_rl].reshape(-1, 1)
y_rl = y_rl[mask_rl]

model_rl = LinearRegression()
model_rl.fit(X_rl, y_rl)
y_pred_rl = model_rl.predict(X_rl)

coef_rl = model_rl.coef_[0]
inter_rl = model_rl.intercept_
r2_rl    = r2_score(y_rl, y_pred_rl)
rmse_rl  = np.sqrt(mean_squared_error(y_rl, y_pred_rl))
corr_rl  = np.corrcoef(X_rl.flatten(), y_rl)[0, 1]

print(f"Coeficiente angular (a): {coef_rl:.4f}")
print(f"Intercepto (b):          {inter_rl:.4f}")
print(f"R²:                      {r2_rl:.4f}")
print(f"RMSE:                    {rmse_rl:.2f}")
print(f"Correlação de Pearson:   {corr_rl:.4f}")
print(f"N municípios:            {len(X_rl)}")

fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle("Regressão Linear Simples — Exames de Mamografia: 2023 vs 2024",
             fontsize=13, fontweight='bold')

ax = axes[0]
ax.scatter(X_rl, y_rl, alpha=0.3, color='steelblue', s=15, label='Municípios')
ax.plot(X_rl, y_pred_rl, color='red', linewidth=2, label=f'y = {coef_rl:.3f}x + {inter_rl:.1f}')
ax.set_xlabel('Exames 2023'); ax.set_ylabel('Exames 2024')
ax.set_title(f'Dispersão e Reta de Regressão\nR² = {r2_rl:.4f}'); ax.legend(); ax.grid(True, alpha=0.3)

ax = axes[1]
res_rl = y_rl - y_pred_rl
ax.scatter(y_pred_rl, res_rl, alpha=0.3, color='darkorange', s=15)
ax.axhline(0, color='red', linewidth=1.5, linestyle='--')
ax.set_xlabel('Valores Ajustados'); ax.set_ylabel('Resíduos')
ax.set_title('Resíduos vs Valores Ajustados'); ax.grid(True, alpha=0.3)

ax = axes[2]
ax.hist(res_rl, bins=50, color='mediumpurple', edgecolor='white', alpha=0.8)
ax.axvline(0, color='red', linewidth=1.5, linestyle='--')
ax.set_xlabel('Resíduo'); ax.set_ylabel('Frequência')
ax.set_title('Distribuição dos Resíduos'); ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('grafico_regressao_linear.png', dpi=150, bbox_inches='tight')
plt.show()
print("Gráfico Regressão Linear salvo!")


# 3 REGRESSÃO MÚLTIPLA
print("\n" + "=" * 60)
print("  MODELO 3: Regressão Múltipla")
print("=" * 60)

mask_rm  = y_num < y_num.quantile(0.99)
X_rm     = X_full[mask_rm]
y_rm     = y_num[mask_rm]

X_train_rm, X_test_rm, y_train_rm, y_test_rm = train_test_split(
    X_rm, y_rm, test_size=0.30, random_state=42
)

scaler_rm  = StandardScaler()
Xtr_rm     = scaler_rm.fit_transform(X_train_rm)
Xte_rm     = scaler_rm.transform(X_test_rm)

model_rm       = LinearRegression()
model_rm.fit(Xtr_rm, y_train_rm)
y_pred_rm_tr   = model_rm.predict(Xtr_rm)
y_pred_rm_te   = model_rm.predict(Xte_rm)

n_rm     = len(y_train_rm)
p_rm     = Xtr_rm.shape[1]
r2_tr_rm = r2_score(y_train_rm, y_pred_rm_tr)
r2_te_rm = r2_score(y_test_rm,  y_pred_rm_te)
r2_adj_rm= 1 - (1 - r2_tr_rm) * (n_rm - 1) / (n_rm - p_rm - 1)
rmse_rm  = np.sqrt(mean_squared_error(y_test_rm, y_pred_rm_te))

print(f"R² treino:    {r2_tr_rm:.4f}")
print(f"R² ajustado:  {r2_adj_rm:.4f}")
print(f"R² teste:     {r2_te_rm:.4f}")
print(f"RMSE:         {rmse_rm:.2f}")

Xtr_const  = np.column_stack([np.ones(n_rm), Xtr_rm])
beta_hat   = np.linalg.lstsq(Xtr_const, y_train_rm, rcond=None)[0]
res_hat    = y_train_rm.values - Xtr_const @ beta_hat
sigma2     = np.sum(res_hat**2) / (n_rm - p_rm - 1)
se_rm      = np.sqrt(np.diag(sigma2 * np.linalg.inv(Xtr_const.T @ Xtr_const)))
t_rm       = beta_hat / se_rm
pv_rm      = 2 * stats.t.sf(np.abs(t_rm), df=n_rm - p_rm - 1)

print(f"\n{'Feature':<25} {'Coef':>10} {'Std Err':>10} {'t':>8} {'p-valor':>10} {'Sig':>5}")
print("─" * 75)
for name, coef, s, t, pv in zip(['intercepto']+list(X_rm.columns), beta_hat, se_rm, t_rm, pv_rm):
    sig = '***' if pv < 0.001 else '**' if pv < 0.01 else '*' if pv < 0.05 else ''
    print(f"{name:<25} {coef:>10.4f} {s:>10.4f} {t:>8.3f} {pv:>10.4f} {sig:>5}")

alphas_rm    = [0.001, 0.01, 0.1, 1, 10, 100, 1000]
ridge_r2_rm  = []
lasso_r2_rm  = []
ridge_coefs_rm = []

print(f"\n{'alpha':>8} | {'Ridge R²':>10} | {'Lasso R²':>10}")
print("─" * 35)
for a in alphas_rm:
    r = Ridge(alpha=a).fit(Xtr_rm, y_train_rm)
    l = Lasso(alpha=a, max_iter=10000).fit(Xtr_rm, y_train_rm)
    rr = r2_score(y_test_rm, r.predict(Xte_rm))
    lr = r2_score(y_test_rm, l.predict(Xte_rm))
    ridge_r2_rm.append(rr); lasso_r2_rm.append(lr); ridge_coefs_rm.append(r.coef_)
    print(f"{a:>8} | {rr:>10.4f} | {lr:>10.4f}")

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle("Regressão Múltipla — Exames de Mamografia (2025)", fontsize=14, fontweight='bold')

ax = axes[0, 0]
ax.scatter(y_test_rm, y_pred_rm_te, alpha=0.3, s=15, color='steelblue')
mn, mx = min(y_test_rm.min(), y_pred_rm_te.min()), max(y_test_rm.max(), y_pred_rm_te.max())
ax.plot([mn, mx], [mn, mx], 'r--', linewidth=2, label='Perfeito')
ax.set_xlabel('Valores Reais'); ax.set_ylabel('Valores Previstos')
ax.set_title(f'Previsto vs Real\nR² = {r2_te_rm:.4f}'); ax.legend(); ax.grid(True, alpha=0.3)

ax = axes[0, 1]
res_rm = y_test_rm.values - y_pred_rm_te
ax.scatter(y_pred_rm_te, res_rm, alpha=0.3, s=15, color='darkorange')
ax.axhline(0, color='red', linewidth=1.5, linestyle='--')
ax.set_xlabel('Valores Previstos'); ax.set_ylabel('Resíduos')
ax.set_title('Resíduos vs Valores Previstos'); ax.grid(True, alpha=0.3)

ax = axes[0, 2]
ax.hist(res_rm, bins=50, color='mediumpurple', edgecolor='white', alpha=0.8)
ax.axvline(0, color='red', linewidth=1.5, linestyle='--')
ax.set_xlabel('Resíduo'); ax.set_ylabel('Frequência')
ax.set_title('Distribuição dos Resíduos'); ax.grid(True, alpha=0.3)

ax = axes[1, 0]
coef_s = pd.Series(model_rm.coef_, index=X_rm.columns)
ax.barh(coef_s.index, coef_s.values, color=['#4CAF50' if v > 0 else '#F44336' for v in coef_s.values])
ax.axvline(0, color='black', linewidth=0.8); ax.set_xlabel('Coeficiente (padronizado)')
ax.set_title('Coeficientes da Regressão Múltipla'); ax.grid(True, alpha=0.3, axis='x')

ax = axes[1, 1]
ax.semilogx(alphas_rm, ridge_r2_rm, marker='o', color='#2196F3', linewidth=2, label='Ridge')
ax.semilogx(alphas_rm, lasso_r2_rm, marker='s', color='#F44336', linewidth=2, label='Lasso')
ax.axhline(r2_te_rm, color='green', linestyle='--', linewidth=1.5, label=f'OLS ({r2_te_rm:.3f})')
ax.set_xlabel('Alpha (log)'); ax.set_ylabel('R² no teste')
ax.set_title('Ridge vs Lasso — Efeito do Alpha'); ax.legend(); ax.grid(True, alpha=0.3)

ax = axes[1, 2]
rc_arr = np.array(ridge_coefs_rm)
for i, name in enumerate(X_rm.columns):
    ax.semilogx(alphas_rm, rc_arr[:, i], linewidth=1.5, label=name)
ax.set_xlabel('Alpha (log)'); ax.set_ylabel('Valor do Coeficiente')
ax.set_title('Trajetória dos Coeficientes — Ridge')
ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
ax.legend(fontsize=7, loc='upper right'); ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('grafico_regressao_multipla.png', dpi=150, bbox_inches='tight')
plt.show()
print("Gráfico Regressão Múltipla salvo!")


# 4 REGRESSÃO LOGÍSTICA
print("\n" + "=" * 60)
print("  MODELO 4: Regressão Logística")
print("=" * 60)

y_log = (pivot[ano_target] >= media_nacional_2025).astype(int)

X_train_lg, X_test_lg, y_train_lg, y_test_lg = train_test_split(
    X_full, y_log, test_size=0.30, random_state=42, stratify=y_log
)

scaler_lg  = StandardScaler()
Xtr_lg     = scaler_lg.fit_transform(X_train_lg)
Xte_lg     = scaler_lg.transform(X_test_lg)

model_lg   = LogisticRegression(max_iter=1000, random_state=42)
model_lg.fit(Xtr_lg, y_train_lg)
y_pred_lg  = model_lg.predict(Xte_lg)
y_prob_lg  = model_lg.predict_proba(Xte_lg)[:, 1]

acc_lg     = (y_pred_lg == y_test_lg).mean()
fpr, tpr, _= roc_curve(y_test_lg, y_prob_lg)
roc_auc    = auc(fpr, tpr)
prec, rec, _= precision_recall_curve(y_test_lg, y_prob_lg)

print(f"Acurácia: {acc_lg:.4f}")
print(f"AUC-ROC:  {roc_auc:.4f}")
print()
print(classification_report(y_test_lg, y_pred_lg, target_names=['Abaixo da média', 'Acima da média']))

coef_lg = pd.Series(model_lg.coef_[0], index=X_full.columns).sort_values()
print("\nCoeficientes (log-odds):")
print(coef_lg.to_string())
print("\nOdds Ratio (exp(coef)):")
print(np.exp(coef_lg).to_string())

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle("Regressão Logística — Mamografia: Prever se município ficará acima da média (2025)",
             fontsize=12, fontweight='bold')

ax = axes[0, 0]
cm = confusion_matrix(y_test_lg, y_pred_lg)
ConfusionMatrixDisplay(cm, display_labels=['Abaixo', 'Acima']).plot(ax=ax, colorbar=False, cmap='Blues')
ax.set_title('Matriz de Confusão')

ax = axes[0, 1]
ax.plot(fpr, tpr, color='#2196F3', linewidth=2, label=f'AUC = {roc_auc:.4f}')
ax.plot([0, 1], [0, 1], 'k--', linewidth=1, label='Aleatório')
ax.fill_between(fpr, tpr, alpha=0.1, color='#2196F3')
ax.set_xlabel('Taxa de Falsos Positivos'); ax.set_ylabel('Taxa de Verdadeiros Positivos')
ax.set_title('Curva ROC'); ax.legend(); ax.grid(True, alpha=0.3)

ax = axes[0, 2]
ax.plot(rec, prec, color='#F44336', linewidth=2)
ax.fill_between(rec, prec, alpha=0.1, color='#F44336')
ax.set_xlabel('Recall'); ax.set_ylabel('Precision')
ax.set_title('Curva Precision-Recall'); ax.grid(True, alpha=0.3)

ax = axes[1, 0]
ax.barh(coef_lg.index, coef_lg.values,
        color=['#4CAF50' if v > 0 else '#F44336' for v in coef_lg.values])
ax.axvline(0, color='black', linewidth=0.8); ax.set_xlabel('Coeficiente (log-odds)')
ax.set_title('Coeficientes da Regressão Logística'); ax.grid(True, alpha=0.3, axis='x')

ax = axes[1, 1]
ax.hist(y_prob_lg[y_test_lg == 0], bins=40, alpha=0.6, color='#FF5722',
        label='Abaixo da média', density=True)
ax.hist(y_prob_lg[y_test_lg == 1], bins=40, alpha=0.6, color='#4CAF50',
        label='Acima da média', density=True)
ax.axvline(0.5, color='black', linestyle='--', linewidth=1.5, label='Limiar = 0.5')
ax.set_xlabel('Probabilidade Prevista'); ax.set_ylabel('Densidade')
ax.set_title('Distribuição das Probabilidades por Classe'); ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

ax = axes[1, 2]
odds = np.exp(coef_lg)
ax.barh(odds.index, odds.values,
        color=['#4CAF50' if v > 1 else '#F44336' for v in odds.values])
ax.axvline(1, color='black', linewidth=0.8, linestyle='--')
ax.set_xlabel('Odds Ratio (exp(coef))'); ax.set_title('Odds Ratio por Preditor')
ax.grid(True, alpha=0.3, axis='x')

plt.tight_layout()
plt.savefig('grafico_regressao_logistica.png', dpi=150, bbox_inches='tight')
plt.show()
print("Gráfico Regressão Logística salvo!")

print("\n" + "=" * 60)
print("  TODOS OS MODELOS CONCLUÍDOS")
print("=" * 60)