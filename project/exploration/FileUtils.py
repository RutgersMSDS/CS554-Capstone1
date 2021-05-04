
def getXGBClassificationScoreFileName():
    return "./output/Class_XGB_SCORES.csv"

def getXGBRegressionScoreFileName():
    return "./output/Reg_XGB_SCORES.csv"


def getXGBClassificationOutputFileName():
    return "./output/Class_XGB_OUTPUT.csv"

def getXGBRegressionOutputFileName():
    return "./output/Reg_XGB_OUTPUT.csv"

def getXGBClassificationConfusionMatrix():
    return "./output/Class_XGB_ConfM.csv"

def getXGBClassificationBinScoreFileName():
    return "./output/Class_XGB_Bins.csv"

def getXGBRegressionHistogramFileName():
    return "./output/Reg_XGB_Histogram.csv"

def clearOutputFolder():
    import os, shutil
    folder = './output'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))