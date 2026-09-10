import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parents[1]/'src'))
from reconstruction import reconstruct

def test_linear_and_edge_extension():
    ex=np.array([300,305,310,315,320]); x=np.array([[0.],[1.],[2.],[3.],[4.]])
    out,s=reconstruct(x,ex,np.ones((5,1),bool),[305,315])
    assert np.allclose(out[:,0],[1,1,2,3,3]); assert np.all(s[:,0]==2)

def test_mask_and_single_support():
    ex=np.array([300,305,310]); x=np.array([[1.],[2.],[3.]])
    valid=np.array([[True],[False],[True]])
    out,s=reconstruct(x,ex,valid,[305])
    assert np.isnan(out[1,0]); assert np.all(s==0) or s[0,0]==0
