# -- coding: utf-8 -- 
from app import create_app
import os
if __name__ == "__main__":
    APP = create_app()
    APP.run(debug=True, port=os.getenv("PORT", default=5000), host='0.0.0.0')
