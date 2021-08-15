from website import createApp
from datetime import datetime
import os,sys

def handledStart():
    try:
        app = createApp()
        if __name__ == "__main__":
            app.run(debug=True,threaded=True)
    except KeyboardInterrupt:
        print("Ctrl + C pressed, now closing")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        file = open("log.txt", "w")
        file.write(f"{current_time}=={e}")
        print("An error occurred, open log file to see more details about error")
    else:
        file = open("log.txt", "w")
        file.write(f"successfully connected")
        print("successfully connected")


def notHandled():
    app = createApp()
    if __name__ == "__main__":
        app.run(debug=True,threaded=True)

notHandled()