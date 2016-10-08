import sys
import json
from libpgm.pgmlearner import PGMLearner
from collections import OrderedDict
# Add to PYTHONPATH
sys.path.append("../")

includeLG = False


class LearnTheStructure(object):
    """Learns the structure and parameters of linear Gaussian model given only
    the data.

        Args:
            pvalparam: Threshold below which significance is unlikely
            bins: The number of bins to discretize the data into.     From the
            libpgm package:
            "The number of bins to discretize the data into. The
            method is to find the highest and lowest value, divide that interval
            uniformly into a certain number of bins, and place the data inside. This
            number must be chosen carefully in light of the number of trials. There
            must be at least 5 trials in every bin, with more if the indegree is
            increased."

        Returns:
            A libpgm object containing structure, parameters and CPD.

    """

    def __init__(self, pvalparam=.05, bins=10, **kw):
        self.data = self.clean_data()
        self.pvalparam = float(pvalparam)
        self.bins = int(bins)
        self.result = self.estimate_discrete_model(self.data)
        if includeLG:
            self.resultlg = self.estimate_lg_model(self.data)

    def run(self):
        print "Bayesian structure learning on the Breast Cancer Dataset using libpgm 1.3"
        print "P-value hyperparameter: ", self.pvalparam
        print "Bins for linear Gaussian: ", self.bins

    def clean_data(self):
        """Converts raw data to libpgm readable JSON and saves the file."""
        raw_data_path = '../data/breast-cancer-wisconsin.data'
        self.define_attributes()
        data = self.convert_to_json(raw_data_path)

        # Loads and cleans the data.
        data_path = '../data/breast-data.txt'
        f = open(data_path, 'r')
        ftext = f.read()
        ftext = ftext.translate(None, '\t\n ')
        ftext = ftext.replace(':', ': ')
        ftext = ftext.replace(',', ', ')
        ftext = ftext.replace('None', 'null')
        # Imputes missing values with hardcoded median value.
        ftext = ftext.replace('?', '1')
        data = json.loads(ftext)
        f.close()

        for d in data:
            del d['Samplecodenumber']

        # Converts unicode strings to int data type.
        clean_data = []
        for d in data:
            clean_data.append(dict((k, int(v)) for k, v in d.iteritems()))

        # Outputs imputed data.
        with open('../data/breast-data-imputed.txt', 'w') as out_file:
            json.dump(clean_data, out_file, indent=2, sort_keys=False,
                      separators=(',', ': '))
        return clean_data

    def define_attributes(self):
        self.attributes = [
            "Sample code number",
            "Clump Thickness",
            "Uniformity of Cell Size",
            "Uniformity of Cell Shape",
            "Marginal Adhesion",
            "Single Epithelial Cell Size",
            "Bare Nuclei",
            "Bland Chromatin",
            "Normal Nucleoli",
            "Mitoses",
            "Class"
        ]

    def convert_to_json(self, path):
        """Converts raw data to json with ordered attributes as keys."""
        json_data = []

        with open(path, "r") as document:
            for line in document:
                values = line.split(",")
                # Remove the line return character "\n"
                values[-1] = values[-1].strip()
                if not line:
                    continue
                json_data.append(
                    {a: v for a, v in zip(self.attributes, values)})

        ordered_data = [OrderedDict(sorted(item.iteritems(), key=lambda (k, v): self.attributes.index(k))) for item in json_data]
        with open('../data/breast-data.txt', 'w') as out_file:
            json.dump(ordered_data, out_file, indent=2, sort_keys=False,
                      separators=(',', ': '))
        return json_data

    def estimate_discrete_model(self, data):
        """Learn the structure and parameters of a discrete Bayesian network.

        Args:
            data: A JSON-style list of dictionaries representing instances.

        Returns:
            A libpgm object containing structure and parameters.
        """
        learner = PGMLearner()

        resultdc = learner.discrete_constraint_estimatestruct(
            data, self.pvalparam)

        # Saves resulting structure.
        if len(sys.argv) > 1:
            with open('../data/breast-data-result-' + str(self.pvalparam) + '.txt', 'w') as out_file:
                json.dump(resultdc.V, out_file, indent=2, sort_keys=False,
                          separators=(',', ': '))
        else:
            with open('../data/breast-data-result.txt', 'w') as out_file:
                json.dump(resultdc.V, out_file, indent=2, sort_keys=False,
                          separators=(',', ': '))
        print "Linear Gaussian Demo"
        print "Edges model:"
        print json.dumps(resultdc.E, indent=2)
        print "Vertices:"
        print json.dumps(resultdc.V, indent=2)
        return resultdc

    def estimate_lg_model(self, data):
        """Estimates the structure and parameters of linear Gaussian model.

        Args:
            data: A JSON-style list of dictionaries representing instances.

        Returns:
            A libpgm object containing structure and parameters.
        """
        learner = PGMLearner()
        resultlg = learner.lg_estimatebn(
            data, self.pvalparam, self.bins, 1)

        return resultlg

if __name__ == '__main__':
    if 'lg' in sys.argv:
        sys.argv.remove('lg')
        includeLG = True
    if len(sys.argv) == 3:
        LearnTheStructure(sys.argv[1], sys.argv[2]).run()
    elif len(sys.argv) == 2:
        LearnTheStructure(sys.argv[1]).run()
    else:
        LearnTheStructure().run()
