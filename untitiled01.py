#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  3 11:32:39 2025

@author: swaralihavaldar
"""

#import packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#load the data
file_path = ("/Users/swaralihavaldar/Documents/PhD/2nd Year/Writing_Communication/ASO/master_tickets.csv")
df = pd.read_csv(file_path)

# Get an overview of subscription vs single ticket buyer
counts = df.groupby(['fiscal_year', 'ticket_type']).size().unstack(fill_value=0)

# Plot
# Define teal color palette
teal_colors = ['#008080', '#20B2AA']

fig, axes = plt.subplots(1, 2, figsize=(10, 5))

for ax, year in zip(axes, counts.index):
    counts.loc[year].plot(
        kind='pie',
        autopct='%1.1f%%',
        startangle=90,
        ax=ax,
        colors=teal_colors,
        title=f"Ticket Type Share - {year}",
        ylabel=''
    )

plt.tight_layout()
plt.show()

#get unique values of price_code_type
df['price_code_type'].unique()
