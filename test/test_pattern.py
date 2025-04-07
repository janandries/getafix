from process import Pattern

def test_pattern():
    #create a  pattern
    p = Pattern((20,20))
    p.add_line(0,0,10)
    for i in range(0,10):
        assert p[0,i] == 1
        assert p[1,i] == 0
        assert p[2,i] == 0
        assert p[5,i] == 0

def test_pattern_out_of_bounds():
    p = Pattern((10,10))
    #with pytest.raises(IndexError):
    p.add_line(0,0,13)

