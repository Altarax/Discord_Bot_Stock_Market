# Librairies
import discord
from discord.ext import commands
from bs4 import BeautifulSoup
import re
import pandas as pd
import random
import urllib.request
import matplotlib.pyplot as plt
import csv
import wikipedia

# Librairies for Degiro API
import degiroapi
from degiroapi.product import Product
from degiroapi.utils import pretty_json
from datetime import datetime, timedelta
import yfinance as yf

wikipedia.set_lang("fr")

# Account to connect to the site "Degiro"
degiro = degiroapi.DeGiro()
degiro.login("", "")

# Choosing my plt style
plt.style.use('classic')

# Colors list for lines in plot
colors_list = ["r", "b", "g", "k", "m", "y", "c"]


def setup(bot):
    bot.add_cog(CogOwner(bot))


class CogOwner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def info(self, ctx, act_name):
        if "-" in act_name:
            act_name_list = act_name.split("-")
            act_name = ' '.join(act_name_list)
        else:
            act_name = act_name

        searched_product = degiro.search_products(act_name)
        devise = Product(searched_product[0]).currency
        realprice = degiro.real_time_price(Product(searched_product[0]).id, degiroapi.Interval.Type.One_Day)
        info_dict = realprice[0]["data"]

        transactions = degiro.transactions(datetime(2019, 1, 1), datetime.now())
        print(pretty_json(transactions))

        await ctx.send(
            f"Le prix de l'action **{act_name.capitalize()}**, est au moment de la réponse à : **{info_dict['lastPrice']} {devise}** \n"
            f"\n"
            f"A l'ouverture l'action était à : **{info_dict['openPrice']} {devise}** \n"
            f"A la clôture, l'action était à : **{info_dict['closePrice']} {devise}** \n"
            f"Le plus haut est de : **{info_dict['highPrice']} {devise}** \n"
            f"Le plus bas est de : **{info_dict['lowPrice']} {devise}**")

    @commands.command()
    async def var(self, ctx, act_name):
        if "-" in act_name:
            act_name_list = act_name.split("-")
            act_name = '%20'.join(act_name_list)
        else:
            act_name = act_name

        searched_product = degiro.search_products(act_name)
        realprice = degiro.real_time_price(Product(searched_product[0]).id, degiroapi.Interval.Type.One_Day)
        devise = Product(searched_product[0]).currency

        # getting historical data
        last_price = realprice[1]['data'][0][1]
        first_price = realprice[1]['data'][-1][1]

        var = last_price - first_price

        if var > 0:
            new_var = (100 * last_price / first_price) - 100
            await ctx.send(f"L'action de {act_name} a gagné : **{'%.4f' % (var)} {devise}** \n"
                           f"Soit : **{'%.4f' % new_var}** %")
        elif var == 0:
            await ctx.send(f"L'action n'a pas bougé")
        else:
            new_var = 100 - (100 * last_price / first_price)
            await ctx.send(f"L'action de {act_name} a perdu de puis l'ouverture : **{'%.4f' % abs(var)} {devise}** \n"
                           f"Soit : **{'%.4f' % new_var} %**")

    @commands.command()
    async def analyses(self, ctx, act_name):
        if "-" in act_name:
            act_name_list = act_name.split("-")
            act_name = ' '.join(act_name_list)
        else:
            act_name = act_name

        ticker = yf.Ticker(act_name)
        reco = ticker.recommendations["To Grade"].value_counts()[0]
        index_reco = ticker.recommendations["To Grade"].value_counts().index.tolist()[0]

        await ctx.send(f"Pour {ticker.info['longName']}, les analystes conseillent en majorité de : **{index_reco}** \n"
                       f"Nombre de conseils : **{reco}**")

    @commands.command()
    async def graph_a(self, ctx, act_name="help", interval=None):
        if "-" in act_name:
            act_name_list = act_name.split("-")
            act_name = ' '.join(act_name_list)
        else:
            act_name = act_name

        if interval == "1D":
            interval_type = degiroapi.Interval.Type.One_Day
        elif interval == "1W":
            interval_type = degiroapi.Interval.Type.One_Week
        elif interval == "1M":
            interval_type = degiroapi.Interval.Type.One_Month
        elif interval == "1Y":
            interval_type = degiroapi.Interval.Type.One_Year
        elif interval == "3Y":
            interval_type = degiroapi.Interval.Type.Three_Years
        elif interval == "5Y":
            interval_type = degiroapi.Interval.Type.Five_Years
        elif interval == "Max":
            interval_type = degiroapi.Interval.Type.Max
        else:
            await ctx.send("Intervalles possibles : \n"
                           "1D (1 jour)\n"
                           "1W \n"
                           "1M \n"
                           "1Y \n"
                           "3Y \n"
                           "5Y \n"
                           "Max \n")

        searched_product = degiro.search_products(act_name)
        devise = Product(searched_product[0]).currency

        realprice = degiro.real_time_price(Product(searched_product[0]).id, interval_type)

        # Getting the real time price
        print(realprice[0]['data']['lastPrice'])
        print(pretty_json(realprice[0]['data']))

        # Getting Data
        data = realprice[1]['data']

        print(data)

        time_data = [i[0] for i in data]
        price_data = [p[1] for p in data]

        # Graphic
        plt.figure(figsize=(12, 5))
        plt.grid(True)
        plt.plot(time_data, price_data, label=act_name, linewidth=1, color=random.choice(colors_list))
        plt.legend(loc='upper left')
        plt.xlabel('Time (In_something)')
        plt.ylabel(f'Prix de {act_name} {devise}')
        plt.savefig('Graph.png')

        await ctx.send(file=discord.File('Graph.png'))

    @commands.command()
    async def company(self, ctx, act_name):
        if "-" in act_name:
            act_name_list = act_name.split("-")
            act_name = ' '.join(act_name_list)
        else:
            act_name = act_name

        page = wikipedia.page(act_name)
        url = page.url
        page = urllib.request.urlopen(url)
        soup = BeautifulSoup(page, 'html.parser')

        creation = soup.find(class_='nowrap date-lien')
        name_company = soup.find(class_="firstHeading")
        info_box = soup.find('table', {'class': "infobox_v2"})
        tr_rows = info_box.find_all('tr')
        td_rows = info_box.find_all('td')

        td_rows_df = []
        tr_rows_df = []

        for row in tr_rows:
            td_rows_df.append(row.get_text())

        for row in td_rows:
            tr_rows_df.append(row.get_text())

        wiki_information = td_rows_df[-6:-1]

        capitalisation = []
        turnover = []
        results = []

        for i in wiki_information:
            if "Capitalisation" in i:
                capitalisation.append(i)

            elif "Chiffre" in i:
                turnover.append(i)

            elif "Résultat" in i:
                results.append(i)

        capitalisation_str = ' '.join(map(str, capitalisation))
        turnover_str = ' '.join(map(str, turnover))
        results_str = ' '.join(map(str, results))

        await ctx.send(f"Date de création de l'entreprise **{name_company.get_text()}** : **{creation.get_text()}** \n"
                       f"{capitalisation_str[1:15]} : **{capitalisation_str[17:-2]}** \n"
                       f"{turnover_str[1:18]} : **{turnover_str[21:-2]}** \n"
                       f"{results_str[1:13]} : **{results_str[15:-2]}**")

    @commands.command()
    async def div(self, ctx, act_name):
        if "-" in act_name:
            act_name_list = act_name.split("-")
            act_name = ' '.join(act_name_list)
        else:
            act_name = act_name

        ticker = yf.Ticker(act_name)

        # show actions (dividends, splits) : graphic
        plt.figure(figsize=(18, 8))
        plt.grid(True)
        plt.plot(ticker.dividends.index, ticker.dividends, label=act_name, color=random.choice(colors_list))
        plt.legend(loc='upper left')
        plt.title(f"Montant du dividende par action de {ticker.info['longName']} depuis {ticker.dividends.index[0]}")
        plt.xlabel('Date')
        plt.ylabel(f'Prix de {act_name} en {ticker.info["currency"]}')
        plt.savefig('Dividendes.png')

        await ctx.send(file=discord.File('Dividendes.png'))

    @commands.command()
    async def graph_t(self, ctx, act_name="help", interval=None):
        if "-" in act_name:
            act_name_list = act_name.split("-")
            act_name = ' '.join(act_name_list)
        else:
            act_name = act_name

        if act_name == "help":
            await ctx.send("Intervalles possibles : \n"
                           "1d \n"
                           "5d \n"
                           "1mo \n"
                           "3mo \n"
                           "6mo \n"
                           "1y \n"
                           "2y \n"
                           "5y \n"
                           "10y \n"
                           "ytd \n"
                           "max")

        ticker = yf.Ticker(act_name)
        hist = ticker.history(period=interval)
        hist.index = hist.index.date

        # show actions : graphic
        plt.figure(figsize=(18, 8))
        plt.grid(True)
        plt.plot(hist.index, hist["Open"], label=act_name, color=random.choice(colors_list))
        plt.legend(loc='upper right')
        plt.title(f"Montant par action de {ticker.info['longName']} depuis {hist.index[0]}")
        plt.xlabel('Date')
        plt.ylabel(f'Prix de {act_name} en {ticker.info["currency"]}')
        plt.savefig('Actions.png')

        await ctx.send(file=discord.File('Actions.png'))

    @commands.command()
    async def per(self, ctx, act_name):
        if "-" in act_name:
            act_name_list = act_name.split("-")
            act_name = ' '.join(act_name_list)
        else:
            act_name = act_name

        page = wikipedia.page(act_name)
        url = page.url
        page = urllib.request.urlopen(url)
        soup = BeautifulSoup(page, 'html.parser')

        info_box = soup.find('table', {'class': "infobox_v2"})
        tr_rows = info_box.find_all('tr')
        td_rows = info_box.find_all('td')

        td_rows_df = []
        tr_rows_df = []

        for row in tr_rows:
            td_rows_df.append(row.get_text())

        for row in td_rows:
            tr_rows_df.append(row.get_text())

        wiki_information = td_rows_df[-6:-1]

        capitalisation = []
        results = []

        for i in wiki_information:
            if "Capitalisation" in i:
                capitalisation.append(i)

            elif "Résultat" in i:
                results.append(i)

        capitalisation_str = ' '.join(map(str, capitalisation))
        results_str = ' '.join(map(str, results))

        capitalisation_split = capitalisation_str[17:-2].split(" ")
        float_capitalisation = capitalisation_split[0:-3]

        results_split = results_str[15:-2].split(" ")
        float_results = float(results_split[0])

        print(f"{float_results}, {float_capitalisation}")
