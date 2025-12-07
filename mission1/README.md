# 概要

リーダフォロワの概念やテレオペレータの使い方を学びました。小型の AC アダプターを掴み、指定された位置に設置するミッションを行いました。
カメラを三代使用し、様々な画質・フレームレートで学習を行いました。

# 使用したコマンド

```
lerobot-teleoperate \
 --robot.type=so101_follower \
 --robot.port=/dev/ttyACM1 \
 --robot.id=pullup_follower_arm \
 --teleop.type=so101_leader \
 --teleop.port=/dev/ttyACM0 \
 --teleop.id=pullup_leader_arm

front:8 front2:4 front3:6

lerobot-teleoperate \
 --robot.type=so101_follower \
 --robot.port=/dev/ttyACM1 \
 --robot.id=pullup_follower_arm \
 --robot.cameras="{ front: {type: opencv, index_or_path: 8, width: 320, height: 240, fps: 30},front2: {type: opencv, index_or_path: 6, width: 320, height: 240, fps: 30}}" \
 --teleop.type=so101_leader \
 --teleop.port=/dev/ttyACM0 \
 --teleop.id=pullup_leader_arm \
 --display_data=true

lerobot-teleoperate \
 --robot.type=so101_follower \
 --robot.port=/dev/ttyACM1 \
 --robot.id=pullup_follower_arm \
 --robot.cameras="{ front: {type: opencv, index_or_path: 8, width: 640, height: 480, fps: 30}, front2: {type: opencv, index_or_path: 6, width: 640, height: 480, fps: 30}}" \
 --teleop.type=so101_leader \
 --teleop.port=/dev/ttyACM0 \
 --teleop.id=pullup_leader_arm \
 --display_data=true

【セキュリティ注意】機密トークンは平文で保管・共有しないでください。

推奨手順（macOS / zsh）:

```

export HF_TOKEN="$(security find-generic-password -w -a "$USER" -s hf_token 2>/dev/null || echo '<paste-token-here>')"
huggingface-cli login --token "$HF_TOKEN" --add-to-git-credential

```

または、以下のように環境変数を直接設定して使用してください。

```

export HF_TOKEN="<your-hf-token>"
huggingface-cli login --token "$HF_TOKEN" --add-to-git-credential

```

lerobot-record \
 --robot.type=so101_follower \
 --robot.port=/dev/ttyACM1 \
 --robot.id=pullup_follower_arm \
 --robot.cameras="{ front: {type: opencv, index_or_path: 6, width: 640, height: 480, fps: 30}, front2: {type: opencv, index_or_path: 9, width: 640, height: 480, fps: 30}}" \
 --teleop.type=so101_leader \
 --teleop.port=/dev/ttyACM0 \
 --teleop.id=pullup_leader_arm \
 --display_data=true \
 --dataset.repo_id=charokoukuu/record-potato-release-3 \
 --dataset.num_episodes=10 \
 --dataset.single_task="potato system" \
 --dataset.episode_time_s=17 \
 --dataset.reset_time_s=4

lerobot-record \
 --robot.type=so101_follower \
 --robot.port=/dev/ttyACM1 \
 --robot.id=pullup_follower_arm \
 --robot.cameras="{ front: {type: opencv, index_or_path: 6, width: 640, height: 480, fps: 30},front2: {type: opencv, index_or_path: 9, width: 320, height: 240, fps: 30},front3: {type: opencv, index_or_path: 8, width: 320, height: 240, fps: 30}}" \
 --teleop.type=so101_leader \
 --teleop.port=/dev/ttyACM0 \
 --teleop.id=pullup_leader_arm \
 --display_data=true \
 --dataset.repo_id=charokoukuu/record-box-1 \
 --dataset.num_episodes=50 \
 --dataset.single_task="pick box" \
 --dataset.episode_time_s=10 \
 --dataset.reset_time_s=5

lerobot-replay \
 --robot.type=so101_follower \
 --robot.port=/dev/ttyACM1 \
 --robot.id=pullup_follower_arm \
 --dataset.repo_id=charokoukuu/record-potato \
 --dataset.episode=0 # choose the episode you want to replay

lerobot-record \
 --robot.type=so101_follower \
 --robot.port=/dev/ttyACM1 \
 --robot.cameras="{ front: {type: opencv, index_or_path: 4, width: 640, height: 480, fps: 30}, front2: {type: opencv, index_or_path: 8, width: 640, height: 480, fps: 30}}" \
 --robot.id=pullup_follower_arm \
 --display_data=false \
 --dataset.repo_id=charokoukuu/eval_record-potato-release-3-1 \
 --dataset.single_task="potato system release" \
 --policy.path=charokoukuu/record-potato-release-3
```
