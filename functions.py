# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from datetime import datetime

def monthly_country_pollutant(df, countries, cities=False):
    '''This function calculates the monthly aqi average of all the pollutants present in the table for the inserted countries and for all the available years in the dataset.
    It also corrects the median values which are larger than 500 (following the US EPA standard, which ranges from 0-500)
    INPUT: df: pd.DataFrame with columns 'Date', 'Country', 'City', 'median'
            countries: list with the countries to be extracted
            cities: bool if False the output is a pd.DataFrame with the COUNTRY average AQI values per month. If True, the output is a pd.DataFrame with the CITIES AQI average per month
    OUTPUT: '''
    final_df = pd.DataFrame()
   
    pollutants = df.Specie.unique()
    for pollutant in pollutants:
        pollutant_df = df[df.Specie == pollutant]
        for country in countries:
            country_df = pollutant_df[pollutant_df.Country == country]
            
            if not cities:
                years = country_df.Date.dt.year.unique()
                for year in years:
                    year_df = country_df[country_df.Date.dt.year == year]
                    months = year_df.Date.dt.month.unique()
                    for month in months:
                        #Dataframe with all cities for a given country
                        month_country_df = year_df[year_df.Date.dt.month == month]
                        
                        mean_ser = month_country_df['median'] 
                        date_string = '{}/{}'.format(year, month)
                        
                        #Standard deviation
                        std_dev = np.std(month_country_df['median'])
                        no_points = month_country_df.shape[0]
                        
                        std_dev_mean = std_dev/np.sqrt(no_points)
                        
                        ## T-test confidence interval
                        alpha= 0.95
                        error_95th = stats.t.interval(df=no_points-1, alpha=alpha)[1] * std_dev_mean
                        # Note: months that only have one measurement will be given a NaN value by the t-test and thus, won't be taken into account further
                        
                        temp_df = pd.DataFrame(data={'Date':datetime.strptime(date_string, '%Y/%m'), 'Country': country, 'No_points': no_points, 'Specie': pollutant, \
                                                     'AQI': [mean_ser.mean()], 'std_dev': std_dev_mean, 'conf_interval_95%': error_95th})
             
                        #print(temp_df)
                        final_df = pd.concat([final_df, temp_df])
         
                        
            if cities:
                cities_country = country_df.City.unique()
                for city in cities_country:
                    city_df = country_df[country_df.City == city]
                    years = city_df.Date.dt.year.unique()
                    for year in years:
                        year_df = city_df[city_df.Date.dt.year == year]
                        months = year_df.Date.dt.month.unique()
                        for month in months:
                            #Dataframe with a particular city in a given country
                            month_df = year_df[year_df.Date.dt.month == month]
                            
                            mean_ser = month_df['median']
                            date_string = '{}/{}'.format(year, month)
                            
                            #Standard deviation
                            std_dev = np.std(month_df['median'])
                            no_days_per_month = month_df.Date.count()
                            
                            std_dev_mean = std_dev/np.sqrt(no_days_per_month)
                            
                            ## T-test confidence interval
                            alpha= 0.95
                            error_95th = stats.t.interval(df=no_points-1, alpha=alpha)[1] * std_dev_mean
                            # Note: months that only have one measurement will be given a NaN value by the t-test and thus, won't be taken into account further
                            
                            
                            
                            temp_df = pd.DataFrame(data={'Date':datetime.strptime(date_string, '%Y/%m'), 'Country': country, 'City': city, 'Specie': pollutant, 'No_points': no_days_per_month, \
                                                         'AQI': [mean_ser.mean()], 'std_dev': std_dev_mean, 'conf_interval_95%': error_95th})
                            #print(temp_df)
                            final_df = pd.concat([final_df, temp_df])
                        
                        
                           
    return final_df.reset_index().drop('index', axis=1)

def monthly_country_AQI(df):
    #Initialize the correct Dataframe input
    cou_df = monthly_country_pollutant(df, countries=df.Country.unique())
    
    final_df = pd.DataFrame()
    years = np.sort(cou_df.Date.dt.year.unique())
    for year in years:
        year_df = cou_df[cou_df.Date.dt.year == year]
        countries = year_df.Country.unique()
        for country in countries:
            country_df = year_df[year_df.Country == country]
            months = country_df.Date.dt.month.unique()
            for month in months:
                month_df = country_df[country_df.Date.dt.month == month]
                
                max_idx = month_df['AQI'].idxmax()
                overall_monthly_AQI = month_df.loc[max_idx, 'AQI']
                most_present_pollutant = month_df.loc[max_idx, 'Specie']
                std_dev_monthly_AQI = month_df.loc[max_idx, 'std_dev']
                conf_interval_monthly_AQI = month_df.loc[max_idx, 'conf_interval_95%']
                total_no_points = month_df.shape[0]
                no_points = month_df.loc[max_idx, 'No_points']
                
                
                
                date_string = '{}/{}'.format(year, month)
                temp_df = pd.DataFrame({'Date': datetime.strptime(date_string, '%Y/%m'), 'Country': country, 'Total_no_points': total_no_points, 'Most_present_pollutant': most_present_pollutant, \
                                            'No_points': no_points, 'AQI': [overall_monthly_AQI], 'std_dev': std_dev_monthly_AQI, 'conf_interval_95%': conf_interval_monthly_AQI})
                final_df = pd.concat([final_df, temp_df])    
                    
    return final_df.reset_index().drop('index', axis=1)

def yearly_country_AQI(cou_df):
    '''The input for this function must be a dataframe with output from calculate_pollutant_country(cities=False)'''
    cou_df = monthly_country_AQI(df)
    
    final_df = pd.DataFrame()
    years = np.sort(cou_df.Date.dt.year.unique())
    for year in years:
        year_df = cou_df[cou_df.Date.dt.year == year]
        countries = year_df.Country.unique()
        for country in countries:
            country_df = year_df[year_df.Country == country]
           
                
            # Yearly mean of the AQI for a particular pollutant and country
            mean_yearly_AQI = country_df['AQI'].mean() 
                
            # Standard deviation of the mean yearly pollutant. Assuming i.i.d i.e Cov = 0
            std_dev_mean = np.sqrt((country_df.std_dev ** 2).sum())/country_df.shape[0] # Propagation of std. deviations for the mean
            no_points = country_df.shape[0]
                
            total_no_points = country_df.Total_no_points.sum()
            
            #T-test confidence interval calculation
            alpha= 0.95
            error_95th = stats.t.interval(df=no_points-1, alpha=alpha)[1] * std_dev_mean
            
            most_present_pollutant = country_df['Most_present_pollutant'].value_counts()[0]
            
                
              
            date_string = '{}'.format(year)
            temp_df = pd.DataFrame({'Date': datetime.strptime(date_string, '%Y'), 'Country': country, 'Total_no_points': total_no_points, 'Most_present_pollutant': most_present_pollutant, \
                                            'No_points': no_points, 'AQI': [mean_yearly_AQI], 'std_dev': std_dev_mean, 'conf_interval_95%': error_95th})
            final_df = pd.concat([final_df, temp_df])    
                    
    return final_df.reset_index().drop('index', axis=1)

def yearly_country_pollutants(cou_df):
    '''The input for this function must be a dataframe with output from calculate_mean_country(cities=False)'''
    cou_df = monthly_country_pollutant(df, countries=df.Country.unique())
    
    final_df = pd.DataFrame()
    years = np.sort(cou_df.Date.dt.year.unique())
    for year in years:
        year_df = cou_df[cou_df.Date.dt.year == year]
        countries = year_df.Country.unique()
        for country in countries:
            country_df = year_df[year_df.Country == country]
            pollutants = country_df.Specie.unique()
            
            # Calculation of the yearly mean for each pollutant:
            for pollutant in pollutants:
                pollutant_df = country_df[country_df.Specie == pollutant]
                
                # Yearly mean of the AQI for a particular pollutant and country
                mean_yearly_pollutant = pollutant_df['AQI'].mean() 
                
                # Standard deviation of the mean yearly pollutant. Assuming i.i.d i.e Cov = 0
                std_dev_mean = np.sqrt((pollutant_df.std_dev ** 2).sum())/pollutant_df.shape[0] # Propagation of std. deviations for the mean
                no_points = pollutant_df.shape[0]
                
                total_no_points = pollutant_df.No_points.sum()
                #T-test confidence interval calculation
                alpha= 0.95
                error_95th = stats.t.interval(df=no_points-1, alpha=alpha)[1] * std_dev_mean
                
                # Calculation of the overall AQI (max of the individual pollutant AQIs)
                
                date_string = '{}'.format(year)
                temp_df = pd.DataFrame({'Date': datetime.strptime(date_string, '%Y'), 'Country': country, 'Total_no_points': total_no_points, \
                                            'No_points': no_points, 'Pollutant': pollutant, 'AQI': [mean_yearly_pollutant], 'std_dev': std_dev_mean, 'conf_interval_95%': error_95th})
                final_df = pd.concat([final_df, temp_df])    
                    
    return final_df.reset_index().drop('index', axis=1)

def yearly_world_AQI(df):
    '''The input for this function must be a dataframe with output from calculate_mean_country(cities=False)'''
    yearly_cou_df = yearly_country_AQI(df)
    
    final_df = pd.DataFrame()
    years = np.sort(yearly_cou_df.Date.dt.year.unique())
    for year in years:
        year_df = yearly_cou_df[yearly_cou_df.Date.dt.year == year]
        
        # World mean AQI:
        mean_world_AQI = year_df.AQI.mean()
        
        # Standard deviation:
        std_dev_mean = np.sqrt((year_df.std_dev ** 2).sum())/year_df.shape[0] # Propagation of standard deviation for the mean
        no_points = year_df.shape[0]
        
        total_no_points = year_df.Total_no_points.sum()
        
        # T-test confidence interval
        alpha= 0.95
        error_95th = stats.t.interval(df=no_points-1, alpha=alpha)[1] * std_dev_mean
        
        
        date_string = '{}'.format(year)
        temp_df = pd.DataFrame({'Date': datetime.strptime(date_string, '%Y'), 'Total_no_points': total_no_points, 'Most_present_pollutant': year_df.Most_present_pollutant.value_counts().index[0], \
                                'No_points': no_points, 'Mean_AQI': [mean_world_AQI], 'std_dev': std_dev_mean, 'conf_interval_95%': error_95th})
        final_df = pd.concat([final_df, temp_df])
    
    return final_df.reset_index().drop('index', axis=1)