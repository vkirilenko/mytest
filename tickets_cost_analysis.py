def q1(x):
    return x.quantile(0.25)

def q2(x):
    return x.quantile(0.75)

df_agg = df_src.groupby(["uploaddate", "route", "route_name"]).agg({
  "price_round": ["mean", "median","std", q1,q2]
}).sort_values(['route','uploaddate'], ascending=True).reset_index()

df_agg.columns = ["uploaddate","route", "route_name", "mean", "median", "std", "q1", "q2"]
df_agg

df_zsc = df_src.merge(df_agg, how = 'left', left_on=['uploaddate', 'route','route_name'], right_on=['uploaddate', 'route','route_name'])
df_zsc['z_score'] = (df_zsc['price_round']-df_zsc['mean'])/df_zsc['std']
df_zsc

plt.figure(figsize=(12, 9))
N = 1500
y = np.linspace(-4, 4, N)
for i in ROUTES.index:
    plt.subplot(3, 4, i+1)
    df_0tmp = df_zsc.loc[df_zsc['route'] == ROUTES.iloc[i,1]]
    plt.hist(df_0tmp["z_score"] ,bins = 120, alpha=0.8, label = ROUTES.iloc[i,2])
    plt.plot(y, stats.norm.pdf(y)*N, '--', alpha=0.8)
    plt.ylim([0, N/3*2])
    plt.yticks(np.arange(0, N/3*2+1, 300))
    plt.xlim([-4, 4])
    plt.legend(fontsize=8, loc='upper center')

plt.show()

plt.figure(figsize=(12, 9))

#cost change
for i in ROUTES.index:
    plt.subplot(3, 4, i+1)
    df_1tmp = df_agg.loc[df_agg['route'] == ROUTES.iloc[i,1]]

    plt.fill_between(df_1tmp['uploaddate'], df_1tmp['q1'], df_1tmp['q2'],
                    facecolor='r',
                    alpha = 0.3,
                    color = 'grey',
                    linewidth = 2,
                    linestyle = '--')
    plt.plot(df_1tmp['uploaddate'],df_1tmp['median'],linewidth = 2, label = ROUTES.iloc[i,2])
    plt.plot(df_1tmp['uploaddate'],df_1tmp['mean'],linewidth = 1)
    plt.legend(fontsize=10, loc='upper center')
    plt.xticks(['2021-04-01','2021-06-01','2021-08-01'],['01-apr','01-jun','01-aug'], fontsize=8)
    plt.yticks(np.arange(0, 10000+100, 3000), fontsize=8)
    plt.ylim([1000, 11000])
    plt.grid()

plt.show()

df_q30 = df_src[df_src['day_bef_dep'] == -15].reset_index()

#time cost changing
plt.figure(figsize=(12, 9))
for i in ROUTES.index:
    plt.subplot(3, 4, i+1)
    df_3tmp = df_q30.loc[df_q30['route'] == ROUTES.iloc[i,1]]
    plt.plot(df_3tmp['dep_date'],df_3tmp['price_round'],linewidth = 2, alpha = 0.8, label = ROUTES.iloc[i,2])
    plt.legend(fontsize=10, loc='upper center')
    plt.xticks(['2021-04-15','2021-06-01','2021-07-15'],['15-apr','01-jun','15-jul'], fontsize=8)
    plt.yticks(np.arange(0, 12000+500, 3000), fontsize=8)
    plt.ylim([1000, 12500])
    plt.grid()
    
plt.show()

week_type = pd.Series(['К. сезонности внутринедельный','Неделя 1 Мая','Неделя 9 Мая','Неделя День России'])

df_q30 = df_src[df_src['day_bef_dep'] == -15].reset_index()
df_q30.loc[(df_q30['route'] == 'KZN -> LED') | (df_q30['route'] == 'KZN -> VKO'), 'dep_date'] += dt.timedelta(days=1)

df_q30.loc[(df_q30['dep_date'] >= '2021-04-26') & (df_q30['dep_date'] <= '2021-05-02'), 'wtype'] = week_type[1]
df_q30.loc[(df_q30['dep_date'] >= '2021-05-03') & (df_q30['dep_date'] <= '2021-05-09'), 'wtype'] = week_type[2]
df_q30.loc[(df_q30['dep_date'] >= '2021-06-07') & (df_q30['dep_date'] <= '2021-06-13'), 'wtype'] = week_type[3]
df_q30.wtype = df_q30.wtype.fillna(week_type[0])

df_q30['day_of_week'] = df_q30['dep_date'].dt.day_name()
df_q30['day_of_week_number'] = df_q30['dep_date'].dt.dayofweek
df_q30.reset_index()

plt.figure(figsize=(14, 10))

for i in week_type.index:
    plt.subplot(2, 2, i+1)
    df_4tmp = df_q30.loc[df_q30['wtype'] == week_type[i]]

    df_q31 = df_4tmp.groupby(["day_of_week", "route_name", "day_of_week_number"]).agg({
      "price_round": ["mean"]
    }).sort_values(['route_name','day_of_week_number'], ascending=True).reset_index()
    df_q31.columns = ["day_of_week","route_name", "day_of_week_number", "price_round"]

    df_q32 = df_4tmp.groupby(["route_name"]).agg({
      "price_round": ["mean"]
    }).sort_values(['route_name'], ascending=True).reset_index()
    df_q32.columns = ["route_name", "price_round_mean"]

    df_q33 = df_q31.merge(df_q32, how = 'left', left_on=['route_name'], right_on=['route_name'])
    df_q33['seasonality'] = df_q33['price_round'] / df_q33['price_round_mean']

    df_q33 = pd.pivot_table(df_q33, values='seasonality', index=['route_name'], columns=['day_of_week_number','day_of_week'], aggfunc=np.mean, fill_value=0)
    df_q33.columns = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    sns.heatmap(df_q33, cmap='RdYlGn_r', annot=True, fmt ='.2g', vmin=0.8, vmax=1.2, center= 1, cbar=True)
    plt.title(week_type[i])
    
plt.show()


df_q40 = df_src[df_src['uploaddate'] >= '2021-04-01'].reset_index()
df_q40 = pd.pivot_table(df_q40, values='price_round', index=['day_bef_dep'], columns=['route_name'], aggfunc=np.mean, fill_value=0)
df_q40 = (df_q40/df_q40.median(axis=0)-1).T

plt.figure(figsize=(12, 5))
sns.heatmap(df_q40, cmap='RdYlGn_r', annot=False,vmin=-0.2, vmax=0.2, center= 0)
plt.title('Лучшее время покупки билетов')
plt.xlabel('Дней до вылета')
plt.ylabel('Направления')
plt.show()