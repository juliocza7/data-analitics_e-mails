import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import email
from email.header import decode_header
import squarify
from math import log, floor

def limpiar_fecha(x):
    if ',' not in x: x = ', ' + x
    if '(' in x: x = ' '.join(x.split(' ')[:-1])
    x = ' '.join(x.split(' ')[:-1])
    return x

def obtener_correo_de_from(x):
    x_mod = x.split('<')[-1].split('>')[0]
    return x_mod

def obtener_nombre_de_from(x):
    text, encoding = decode_header(x)[0]
    if not encoding and isinstance(text, str):
        text = ' '.join(text.split(' ')[:-1])
    else:
        text = text.decode('utf-8', errors='ignore')
        
    text = text.replace('"', '')
    return text

def limpiar_subject(x):
    if x:
        text, encoding = decode_header(x)[0]
        try: text = text.decode('utf-8', errors='ignore')
        except: pass
    else: text=x
    return text


#################visualization

def format(number):
    units = ['', 'K', 'M', 'G', 'T', 'P']
    k = 1000
    magnitude = int(floor(log(number, k)))
    return '%.1f%s' % (number / k**magnitude, units[magnitude])


def plot_emails_x_year(df_emails):
    cont = df_emails['Date'].dt.year.value_counts().to_frame('cantidad')#.plot(kind='bar', figsize=(10, 6)) [df_emails['Date'].dt.year.unique()]
    grouped_df = cont.reset_index()
    grouped_df = grouped_df.sort_values('index', ascending=True)
    print(grouped_df)
    
    loc = [0,1,2,3,4]

    grouped_df['cantidad'].plot(kind='bar', color = '#FF0000', figsize=(10, 6))

    for i in range(len(grouped_df)):
        plt.text(loc[i], grouped_df.iloc[i]['cantidad'], format(grouped_df.iloc[i]['cantidad']), ha = 'center')

    plt.xticks(loc,grouped_df['index'],rotation=0)
    plt.grid(color = 'gray',axis = 'y', linestyle = '--', linewidth = 0.4)
    plt.title('e-mails per year')
    plt.ylabel('quantity')
    plt.show()

def plot_emails_x_month(df_emails):
    cont = df_emails.groupby([df_emails.Date.dt.month.rename('month'), df_emails.Date.dt.year.rename('year')]).size().to_frame('cantidad')
    grouped_df = cont.reset_index()
    pivot = pd.pivot_table(data=grouped_df, index=['month'], columns=['year'], values='cantidad')

    ax = pivot.plot.bar(stacked=True, color =['lightseagreen', 'tomato', 'blue', 'green', 'red'], figsize=(10,6.5))
    ax.set_title('e-mails per month and year', x=0.5, y=1.08, fontsize = 20)
    ax.set_xticklabels(['jan','fev','mar','apr','may','jun','jul','ago','sep','oct','nov','dec'], rotation=0)
    ax.grid(color = 'gray',axis = 'y', linestyle = '--', linewidth = 0.4)
    ax.set_ylabel('quantity')
    ax.legend(loc="lower right", bbox_to_anchor=(1., 1.02) , borderaxespad=0., ncol=5)
    for c in ax.containers:
        ax.bar_label(c, label_type='center')
    plt.show()

def plot_emails_x_day(df_emails):

    df_grouped = df_emails.groupby(['WeekDay']).size().to_frame('cantidad').reset_index()

    ind = pd.Index(['6','2','7','1','5','3','4'])
    loc = [0,1,2,3,4,5,6]
    days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
    df_grouped = df_grouped.set_index(ind).sort_index()

    df_grouped.plot(kind='barh', color = '#008000', legend=None, figsize=(10, 6)) 
 
    plt.yticks(loc,days,rotation=0)
    plt.title('e-mails per day')
    plt.ylabel('e-mails quantity')
    plt.grid(color = 'gray',axis = 'x', linestyle = '--', linewidth = 0.4)

    for i in range(len(df_grouped['cantidad'])):
        plt.text(df_grouped.iloc[i]['cantidad'], loc[i], df_grouped.iloc[i]['cantidad'])

    plt.show()

def plot_emails_x_hour(df_emails):
    df_grouped = df_emails.groupby(['Hour']).size().to_frame('cantidad').reset_index()

    ax = df_grouped.plot(kind='area',style='.-', legend=None, figsize=(10,6))
    ax.set_xticks(np.arange(len(df_grouped['Hour'])))
    ax.set_xticklabels(df_grouped['Hour'], rotation=45)
    ax.grid(color = 'gray',axis = 'y', linestyle = '--', linewidth = 0.4)
    ax.set_title('e-mails per Hour')
    ax.set_ylabel('quantity')

    for i in range(len(df_grouped['Hour'])):
        plt.text(df_grouped.index[i], df_grouped.iloc[i]['cantidad'], df_grouped.iloc[i]['cantidad'], ha = 'center')
    
    plt.show()

def plot_commonwords(df_emails):

    colors = ['#91DCEA', '#0000FF', '#5FBB68', '#F9D23C', '#F9A729', '#FD6F30', '#CD5C5C', '#808000', '#FF00FF', '#008080']

    df_grouped = df_emails.groupby(['Name']).size().to_frame('cantidad').reset_index()
    df_grouped = df_grouped.sort_values('cantidad', ascending=False).iloc[:10]
    df_grouped["label"] = df_grouped["Name"] + ' \n' + df_grouped["cantidad"].astype(str)

    # Treemap
    squarify.plot(sizes = df_grouped['cantidad'], label = df_grouped['label'],
                color = colors, pad = 0.1, alpha = 0.7)

    plt.axis("off")
    plt.title('Top 10 senders')
    plt.show()
    

if __name__ == "__main__":
    df_emails = pd. read_csv ('/home/oem/DataScience/DataAnalitics_gmail/csv/dataset_emails.csv')

    #print(df_emails)

    ### date treatment
    df_emails['Date'] = df_emails['Date'].apply(lambda x: limpiar_fecha(x)) # get "Wed, 14 Sep 2022 17:38:23"
    df_emails['Date'] = df_emails['Date'].str.split(', ').str[-1]           # get "14 Sep 2022 17:38:23"
    df_emails['H_M_S'] = df_emails['Date'].apply(lambda x: x[-8:])          # get "17:38:23"

    df_emails['Hour'] = df_emails['H_M_S'].apply(lambda x: x[:2]+'h-'+str(int(x[:2])+1).zfill(2)+'h')    # get "17h-18h"

    df_emails['Date'] = df_emails['Date'].apply(lambda x: x[:-9] if len(x[:-9])==11 else '0'+x[:-9] )    # get "14 Sep 2022"
    df_emails['Date'] = pd.to_datetime(df_emails['Date'], format='%d %b %Y')                             # get "2022-09-14"
    
    df_emails['WeekDay'] = df_emails['Date'].dt.strftime('%A')                                           # get "Wednesday"  

    #print(df_emails.head())

    #### mails treatment and name and clean subject
    df_emails['Mail'] = df_emails['From'].apply(lambda x: obtener_correo_de_from(x))
    df_emails['Name'] = df_emails['From'].apply(lambda x: obtener_nombre_de_from(x))
    df_emails['Subject'] = df_emails['Subject'].apply(lambda x: limpiar_subject(str(x)))
    df_emails = df_emails.drop(columns=['From'])[['Date','H_M_S','Hour','WeekDay','Mail','Name','Subject']]
    
    #print(df_emails.head())

    #visualization
    plot_emails_x_year(df_emails)
    plot_emails_x_month(df_emails)
    plot_emails_x_day(df_emails)
    plot_emails_x_hour(df_emails)
    plot_commonwords(df_emails)