from config import *
from dbMgr import *

@app.route('/test')
def default():
    populateCurators()
    return render_template('login.html')