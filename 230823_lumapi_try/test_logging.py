for i in range(100):
    try:
        a = 1 / 0
    except ZeroDivisionError:
        print("error")
        break
    finally:
        print("finally")
