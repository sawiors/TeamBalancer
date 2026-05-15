from app import TeamBalancingApp


if __name__ == "__main__":
    app = TeamBalancingApp()
    try:
        app.mainloop()
    except KeyboardInterrupt:
        # Ctrl+C로 종료할 때 불필요한 트레이스백을 숨긴다.
        pass
