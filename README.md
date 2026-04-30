# 2026 CNU Robot AI Class

| Term Project - Mid


### 제작자 정보
> 학번: 202102545<br>
> 프로젝트 명: CNU 차차봇 with 넙죽이 모자<br>
> 기획 의도: 충남대학교를 졸업하고 카이스트 인공지능 대학원 진학을 꿈꿔본다는 의도를 담은 로봇

### 과제 정보
> [TASK.md](./TASK.md) 파일 참조


## 작동 방법

### Git Clone

```bash
git clone https://github.com/b-re-w/cnu_ros_chachabot.git
```

### Colcon Build

```bash
colcon build --symlink-install
```

### Start Robot Launcher

```bash
source install/setup.bash
ros2 launch cnuchacha_launcher cnuchacha.launch.py
```

### Start Robot Controller

```bash
source install/setup.bash
ros2 run cnuchacha_controller cnuchacha_controller
```


## 구현 설명

- 차차봇은 처음에 정자세로 등장해서 팔다리를 앞뒤로 움직인다.
- 키보드로 left/right를 입력하면 넙죽이 모자가 해당 방향으로 회전하기 시작한다.
- 키보드로 up을 입력하면 넙죽이 모자가 위로 점프한다.
- 키보드로 jump를 입력하면 차차봇 전체가 점프한다.
