import numpy as np
from scipy.integrate import odeint
import plotly.graph_objects as go


##################################
###  РЕШАЕМ СИСТЕМУ УРАВНЕНИЙ  ###
##################################

# Система уравнений:
def LorenzMod1(XYZ, t, alpha, beta, xi, delta):
    x, y, z = XYZ
    x_dt = -alpha*x + y*y - z*z + alpha*xi
    y_dt = x*(y - beta*z) + delta
    z_dt = -z + x*(beta*y + z)
    return x_dt, y_dt, z_dt

# Параметры системы и начальные условия:
alpha = 0.1
beta = 4
xi = 14
delta = 0.08



#1111111111111111111111111111111
x_0, y_0, z_0 = 0, 1, 0
print ("1")


# Максимальное время и общее количество
# временных точек:
tmax, n = 100, 40000

# Интегрируем систему уравнений в каждой точке
# временного интервала t:

t = np.linspace(0, tmax, n)
c = np.linspace(0, 1, n)



f = odeint(LorenzMod1, (x_0, y_0, z_0),t,  args=(alpha, beta, xi, delta))
X, Y, Z = f.T

# Параметры системы и начальные условия:
alpha = 0.1
beta = 4
xi = 14
delta = 0.08
#111111111111111111111111111111111111111111111111111111111111111111111






#2222222222222222222222
for ii in range(100001,100005,1):

    i=ii/100000.0
    print (i)
    x_0, y_0, z_0 = 0, i, 0

    # Максимальное время и общее количество
    # временных точек:
    tmax, n = 100, 40000

    # Интегрируем систему уравнений в каждой точке
    # временного интервала t:
    t = np.linspace(0, tmax, n)
    c1 = np.linspace(0, 1, n)


    f = odeint(LorenzMod1, (x_0, y_0, z_0),t,  args=(alpha, beta, xi, delta))
    X1, Y1, Z1 = f.T

  
    X=np.hstack((X1, X))    
    Y=np.hstack((Y1, Y))    
    Z=np.hstack((Z1, Z))    
    c=np.hstack((c1, c))    
#22222222222222222222222222222222222222222222222222222222222222222222
  




#######################
###  ВИЗУАЛИЗИРУЕМ  ###
#######################

# Массив, отвечающий за изменение цвета:


                                            #c = np.linspace(0, 1, len(X))

# Готовим данные для отрисовки:
DATA = go.Scatter3d(x=X, y=Y, z=Z,
                    line=dict(color= c,
                              width=3,
                              # Выбираем цветовую палитру:
                              # Greys,YlGnBu,Greens,YlOrRd,Bluered,RdBu,
                              # Reds,Blues,Picnic,Rainbow,Portland,Jet,
                              # Hot,Blackbody,Earth,Electric,Viridis,Cividis.
                              colorscale="Cividis"),
                    #  Рисуем только линии:
                    mode='lines')

fig = go.Figure(data=DATA)    

# Задаем параметры отрисовки:
fig.update_layout(width=1000, height=1000,
                  margin=dict(r=10, l=10, b=10, t=10),
                  # Устанавливаем цвет фона:
                  paper_bgcolor='rgb(0,0,0)',
                  scene=dict(camera=dict(up=dict(x=0, y=0, z=1),
                                         eye=dict(x=0, y=1, z=1)),
                             # Устанавливаем пропорциональное
                             # соотношение осей друг к другу:
                             aspectratio = dict(x=1, y=1, z=1),
                             # Отображаем, как указано в "aspectratio"
                             aspectmode = 'manual',
                             # Скрываем оси:
                             xaxis=dict(visible=False),
                             yaxis=dict(visible=False),
                             zaxis=dict(visible=False)
                            )
                 )

######################
#!!  ВОСТОРГАЕМСЯ  !!#
######################

fig.show()