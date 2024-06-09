if __name__ == '__main__':
    import MetaTrader5 as mt5

    if not mt5.initialize():
        print("failed to initialized mt5 {}".format(mt5.last_error()))
        quit()
