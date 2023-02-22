#!/usr/bin/env python3

from matplotlib import pyplot as plt


class Plot:
    def __init__(self, rocketPoolDF, unmatchedDF):
        self._rocketPoolDF = rocketPoolDF
        self._unmatchedDF = unmatchedDF

    def drawValues(self):
        y_offset = -5
        for bar in plt.gca().patches:
            ax = plt.gca()
            if (bar.get_height() < 5):
                continue
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + bar.get_y() + y_offset,
                '{:.2f}%'.format(bar.get_height()),
                ha='center',
                color='black',
                weight='bold',
                fontsize=8
            )

    def setTitleAndLabels(self, title, xlabel, ylabel):
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

    def plotBarChart(self, df, title, xlabel, ylabel):
        columns = ['f_client', 'proba_Lighthouse',
                   'proba_Nimbus', 'proba_Prysm', 'proba_Teku']

        # get the distribution of the clients guesses thanks to the mean values
        distribution = df[columns].groupby('f_client').mean()

        # change from decimal to percentage
        percentDistribution = distribution.div(
            distribution.sum(axis=1), axis=0) * 100

        # plot the bar chart
        percentDistribution.plot(kind='bar', stacked=True, title=title)

        # change the titles and labels
        self.setTitleAndLabels(title, xlabel, ylabel)

        # draw the values on the bars
        self.drawValues()

    def getVisualRepresentation(self):
        # plot the distribution of the clients for all the blocks
        self.plotBarChart(self._rocketPoolDF, 'Distribution of the clients guesses for all the blocks',
                     'Clients', 'Percentage (%)')

        # plot the distribution of the clients for the unmatched blocks
        self.plotBarChart(self._unmatchedDF, 'Distribution of the clients guesses for the unmatched blocks',
                     'Clients', 'Percentage (%)')
        plt.show()

    def getMatchingPercentageForEach(self):
        col = ['f_client', 'match']
        res = self._rocketPoolDF[col]
        res = res.groupby('f_client').mean().round(4) * 100
        print(f'\n{res}\n')

    def plot(self):
        self.getVisualRepresentation()
        self.getMatchingPercentageForEach()
