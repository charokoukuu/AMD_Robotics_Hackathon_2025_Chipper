import time
from lerobot.robots.so101_follower.config_so101_follower import SO101FollowerConfig
from lerobot.robots.so101_follower.so101_follower import SO101Follower

# ❶ SO-101 ロボット設定
robot_config = SO101FollowerConfig(
    port="/dev/ttyACM1",
    id="pullup_follower_arm",
)

# ロボットを初期化して接続
robot = SO101Follower(robot_config)
robot.connect()

# 現在の位置を取得
print("現在の位置を読み取り中...")
current_obs = robot.get_observation()
current_pos = {k: v for k, v in current_obs.items() if k.endswith(".pos")}
print("現在の位置:")
for key, val in current_pos.items():
    print(f"  {key}: {val:.2f}°")

# ❲ 目標角度（度）
joint_deg = {
    "shoulder_pan.pos": -54.05,
    "shoulder_lift.pos": -86.62,
    "elbow_flex.pos": 99.82,
    "wrist_flex.pos": 32.17,
    "wrist_roll.pos": -2.72,
    "gripper.pos": 68.19,
}

print("\n目標位置:")
for key, val in joint_deg.items():
    current_val = current_pos.get(key, 0)
    diff = val - current_val
    print(f"  {key}: {val:.2f}° (差: {diff:+.2f}°)")

# ❸ ロボットにコマンドを送る
print("\nロボットを指定位置に移動中...")
action_sent = robot.send_action(joint_deg)
print(f"送信されたアクション: {action_sent}")

# 動作完了まで待機
print("動作完了を待機中...")
time.sleep(3)

# 最終位置を確認
final_obs = robot.get_observation()
final_pos = {k: v for k, v in final_obs.items() if k.endswith(".pos")}
print("\n最終位置:")
for key, val in final_pos.items():
    target_val = joint_deg.get(key, 0)
    diff = val - target_val
    print(f"  {key}: {val:.2f}° (目標との差: {diff:+.2f}°)")

# ロボットを切断
robot.disconnect()
print("\n完了")
