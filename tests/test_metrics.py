import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parents[1]/'src'))
from metrics import reconstruction_metrics

def test_metrics_and_support_accounting():
    x=np.array([[1.,2.],[3.,4.]]); y=x.copy(); mask=np.ones_like(x,bool); support=np.full_like(x,2,dtype=np.int8)
    m=reconstruction_metrics(x,y,mask,support)
    assert m['relative_frobenius_error']==0 and m['reconstruction_supported_fraction']==1 and m['unsupported_fraction']==0

def test_unsupported_not_dropped():
    x=np.ones((2,2)); y=np.array([[1.,np.nan],[1.,np.nan]]); mask=np.ones((2,2),bool); support=np.array([[2,0],[2,0]])
    m=reconstruction_metrics(x,y,mask,support)
    assert m['unsupported_positions']==2 and m['unsupported_fraction']==.5
