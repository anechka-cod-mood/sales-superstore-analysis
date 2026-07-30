#============
#1. LIB IMPORT
#=============
import numpy as np
import pandas as pd
import seaborn as sns
from docx import Document
from tabulate import tabulate
import matplotlib.pyplot as plt

#=============
#2. DATA LOUD
#============
sales=pd.read_csv('data/Sample - Superstore.csv',encoding='latin1')

#===================
#3. Preliminary analysis
#===================
print(sales.head())
sales.info()
print(sales.shape)
print(sales.isnull().sum())
print(sales.columns)
print(sales.duplicated().sum())
print(sales.describe(include='all'))
sales.nunique()

#===========
#4. Category check
print(sales['City'].value_counts())
print(sales['Country'].value_counts())

#====================
#4. Exploratory Data Analysis
#====================

#4.1 Product city analysis
city_and_profit=sales.groupby('City')['Profit'].sum().sort_values(ascending=False)
city_and_sales=sales.groupby('City')['Sales'].sum().sort_values(ascending=False)
sales_and_profit=pd.merge(city_and_profit,city_and_sales, on='City')

print(sales_and_profit.head(10))

sales_and_profit['Margin']=sales_and_profit['Profit']/sales_and_profit['Sales']*100
order_city=sales.groupby('City')['Order ID'].nunique()
sales_and_profit=pd.merge(sales_and_profit,order_city,on='City')

print(tabulate(sales_and_profit.head(10),
               headers='keys',
               tablefmt='tsv')
      )

#4.2 Product category analysis

category_profit=sales.groupby('Category')['Profit'].sum().sort_values(ascending=False)
category_sales=sales.groupby('Category')['Sales'].sum().sort_values(ascending=False)
category_sales_profit=pd.merge(category_profit,category_sales,on='Category')
category_sales_profit['margin,%']=category_sales_profit['Profit']/category_sales_profit['Sales']*100
print(tabulate(category_sales_profit,
               headers='keys',
               tablefmt='tsv')
      )
print(category_sales_profit['Sales'].std())

# 4.3 Sub-Category Analysis

sub_category_sales=sales.groupby('Sub-Category')['Sales'].sum().sort_values(ascending=False)
sub_category_profit=sales.groupby('Sub-Category')['Profit'].sum().sort_values(ascending=False)
sub_category_profit_sales=pd.merge(sub_category_profit,sub_category_sales,on='Sub-Category')
sub_category_profit_sales['margin, %']=sub_category_profit_sales['Profit']/sub_category_profit_sales['Sales']*100

print(tabulate(sub_category_profit_sales,
               headers='keys',
               tablefmt='tsv')
      )

#4.4 Discount Analysis
sales['discount level']=pd.cut(
    sales['Discount'],
    bins=[-0.01, 0, 0.1, 0.2, 0.3, 1],
    labels=['0%','0-10%','11-20%','21-30%','30%+']
)
discount_analysis=sales.groupby('discount level').agg(
    {
    'Profit':'mean',
    'Sales':'sum',
    'Order ID':'nunique'
    }
)
print(tabulate(discount_analysis,
               headers='keys',
               tablefmt='tsv')
      )

#4.5 Discount impact by Category
category_discount=sales.groupby(['Category', 'discount level']).agg(
    {
        'Profit':'mean',
        'Sales':'sum',
        'Order ID':'nunique'
    }
)

print(tabulate(category_discount,
               headers='keys',
               tablefmt='tsv')
      )

#4.6 Time Analysis
print(sales['Order Date'].dtypes)
sales['Order Date']=pd.to_datetime(sales['Order Date'])
sales['Year']=sales['Order Date'].dt.year
sales['Month num']=sales['Order Date'].dt.month
sales['Month']=sales['Order Date'].dt.month_name()
year_results=sales.groupby('Year').agg(
    {
        'Sales':'sum',
        'Profit':'sum',
        'Order ID':'nunique'
    }
)

print(tabulate(year_results,
               headers='keys',
               tablefmt='tsv'
               )
      )
month_result=sales.groupby(['Month num','Month']).agg(
    {
        'Sales':'sum',
        'Profit':'sum',
        'Order ID':'nunique'
    }
)
month_result=month_result.reset_index()
month_result=month_result.sort_values('Month num')
month_result['margin,%']=month_result['Profit']/month_result['Sales']*100
print(tabulate(month_result[['Month','Sales','Profit','Order ID','margin,%']],
               headers='keys',
               tablefmt='tsv',
               showindex=False))

# 4.7 Customer Analysis
customer_analysis=sales.groupby('Segment').agg(
    {
        'Order ID':'nunique',
        'Sales':'sum',
        'Profit':'sum'
    }
)
customer_analysis['margin,%']=customer_analysis['Profit']/customer_analysis['Sales']*100

print(tabulate(customer_analysis,
               headers='keys',
               tablefmt='tsv')
      )
#Customer Segment Analysis
customer_profitability=sales.groupby('Customer Name').agg(
    {
        'Order ID':'nunique',
        'Sales':'sum',
        'Profit':'sum'
    }
)
#Top 10 customers by Profit
customer_profitability['margin,%']=customer_profitability['Profit']/customer_profitability['Sales']*100
customer_profitability=customer_profitability.sort_values('Profit',ascending=False)

print(tabulate(customer_profitability.head(10),
               headers='keys',
               tablefmt='tsv')
      )


#Dangerous customers
customer_profitability=customer_profitability.sort_values('margin,%',ascending=True)
print(tabulate(customer_profitability.head(10),
               headers='keys',
               tablefmt='tsv')
      )

#====================
#5. Visualisation
#====================

# 5.1 Sales by year
year_plot=year_results.reset_index()
plt.figure(figsize=(8,5))
plt.plot(
    year_plot['Year'],
    year_plot['Sales'],
    marker='o',
    linewidth=3,
    markersize=8
)
for x,y in zip(year_plot['Year'], year_plot['Sales']):
    plt.text(x,y,f"{y:,.0f}", ha='center', va='bottom',fontsize=9)

plt.title('Sales by year')
plt.xlabel('Year')
plt.ylabel('Sales')
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    'images/sales_by_year.png',
    dpi=300,
    bbox_inches='tight'
)


# 5.2 Profit by Category
profit_category_plot = category_sales_profit.reset_index()

profit_category_plot=profit_category_plot.sort_values(
    'Profit',
     ascending=False
)

plt.figure(figsize=(8,5))

bars=plt.bar(
    profit_category_plot['Category'],
    profit_category_plot['Profit']
)

plt.title('Profit by Category')
plt.xlabel('Category')
plt.ylabel('Profit ($)')
plt.grid(alpha=0.3)
plt.xticks(rotation=45)

for bar in bars:
    plt.text(
        bar.get_x() + bar.get_width()/2,
        bar.get_height(),
        f'{bar.get_height():,.0f}',
        ha='center',
        va='bottom'
    )

plt.tight_layout()

plt.savefig(
    'images/profit_by_category.png',
    dpi=300,
    bbox_inches='tight'
)
print(customer_analysis)
# 5.3 Profit Margin by Segment
profit_segment_plot=customer_analysis.reset_index()

profit_segment_plot=profit_segment_plot.sort_values(
    'margin,%',
    ascending=False
)
plt.figure(figsize=(8,5))
bars=plt.bar(
    profit_segment_plot['Segment'],
    profit_segment_plot['margin,%']
)

plt.title('Profit Margin by Segment')
plt.xlabel('Segment')
plt.ylabel('Profit Margin (%)')
plt.grid(alpha=0.3)
plt.xticks(rotation=45)

for bar in bars:
    plt.text(
        bar.get_x()+bar.get_width()/2,
        bar.get_height(),
        f'{bar.get_height():,.1f}',
        ha='center',
        va='bottom'
    )
plt.tight_layout()

plt.savefig(
    'images/profit_margin_by_segment.png',
    dpi=300,
    bbox_inches='tight'
)

#5.4 Discount Impact on Profit
print(discount_analysis)
discount_profit_plot=discount_analysis.reset_index()
plt.figure(figsize=(8,5))
bars=plt.bar(
    discount_profit_plot['discount level'],
    discount_profit_plot['Profit']
)
plt.title('Discount Impact on Profit')
plt.xlabel('discount level (%)')
plt.ylabel('Profit')
plt.grid(alpha=0.3)

for bar in bars:
    height = bar.get_height()

    if height >= 0:
        va = 'bottom'
    else:
        va = 'top'

    plt.text(
        bar.get_x() + bar.get_width()/2,
        height,
        f'{height:.1f}',
        ha='center',
        va=va
    )

plt.tight_layout()

plt.savefig(
    'images/discount_impact_on_profit.png',
    dpi=300,
    bbox_inches='tight'
)


# 5.5 Top 10 Cities by Profit

city_profit_plot = sales_and_profit.reset_index()

city_profit_plot = city_profit_plot.head(10)

plt.figure(figsize=(8, 5))

bars = plt.barh(
    city_profit_plot['City'],
    city_profit_plot['Profit']
)

plt.title('Top 10 Cities by Profit')
plt.xlabel('Profit ($)')
plt.ylabel('City')
plt.grid(alpha=0.3)

for bar in bars:
    plt.text(
        bar.get_width() + 500,
        bar.get_y() + bar.get_height() / 2,
        f'{bar.get_width():,.0f}',
        ha='left',
        va='center'
    )

plt.tight_layout()

plt.savefig(
    'images/top_10_cities_by_profit.png',
    dpi=300,
    bbox_inches='tight'
)
plt.show()