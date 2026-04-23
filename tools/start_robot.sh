#!/bin/bash

# 顔色の定義，装飾出力用
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # 無顔色

# 機能：成功メッセージ
print_success() {
    echo -e "${GREEN}$1${NC}"
}

# 機能：情報メッセージ
print_info() {
    echo -e "${YELLOW}$1${NC}"
}

# 機能：エラーメッセージ
print_error() {
    echo -e "${RED}$1${NC}"
}

# 機能：コンポーネントを起動して確認します（最初にROSノードを起動し、次にリアルタイム優先度を設定します）。
start_component() {
    local session_name=$1
    local launch_cmd=$2
    local node_name=$3
    local sleep_time=$4

    print_info "启动 $session_name ..."
    # screenセッションでROSコマンドを開始し、DDS構成環境変数が渡されていることを確認してください。
    screen -dmS $session_name bash -c "source install/setup.bash; export RMW_IMPLEMENTATION='$RMW_IMPLEMENTATION'; export RMW_FASTRTPS_USE_QOS_FROM_XML='$RMW_FASTRTPS_USE_QOS_FROM_XML'; export FASTRTPS_DEFAULT_PROFILES_FILE='$FASTRTPS_DEFAULT_PROFILES_FILE'; $launch_cmd; exec bash"
    sleep $sleep_time

    if ! ros2 node list | grep -q "$node_name"; then
        print_error "$session_name 启动失败！未检测到 $node_name 节点。"
        cleanup_sessions
        exit 1
    fi
}

# 機能: すべてのセッションをクリアする
cleanup_sessions() {
    screen -S inference_session -X quit 2>/dev/null
    screen -S joy_session -X quit 2>/dev/null
}

# 機能：DDS構成が有効かどうかを詳細に検証する。
verify_dds_effectiveness() {
    print_info "DDSの設定が有効かどうかを詳細に確認してください。..."
    sleep 2
    
    # 1. 環境変数を確認する
    print_info "環境変数を確認する..."
    echo "RMW_IMPLEMENTATION: $RMW_IMPLEMENTATION"
    echo "FASTRTPS_DEFAULT_PROFILES_FILE: $FASTRTPS_DEFAULT_PROFILES_FILE"
    
    # 2. 設定ファイルが正しく読み込まれたことを確認してください。
    print_info "設定ファイルの読み取りを確認する..."
    if [ -f "$FASTRTPS_DEFAULT_PROFILES_FILE" ]; then
        print_success "設定ファイルが存在する"
        
        # XML構文をチェックする
        if command -v xmllint &> /dev/null; then
            if xmllint --noout "$FASTRTPS_DEFAULT_PROFILES_FILE" 2>/dev/null; then
                print_success "XML 正常"
            else
                print_error "XML 異常"
                xmllint "$FASTRTPS_DEFAULT_PROFILES_FILE"
                return 1
            fi
        fi
    else
        print_error "設定ファイルが存在しません: $FASTRTPS_DEFAULT_PROFILES_FILE"
        return 1
    fi
    
    # 3. プロセスが使用されているかどうかを確認します Fast DDS
    print_info "チェックプロセスDDS実装..."
    for node in "inference_node" "joy_node"; do
        local pid=$(pgrep -x "$node" 2>/dev/null)
        if [ -n "$pid" ]; then
            # プロセス環境変数を確認する
            local env_file="/proc/$pid/environ"
            if [ -f "$env_file" ]; then
                if grep -z "FASTRTPS_DEFAULT_PROFILES_FILE" "$env_file" >/dev/null 2>&1; then
                    print_success "$node 環境変数は正しく設定されています"
                else
                    print_error "$node 足らない FASTRTPS_DEFAULT_PROFILES_FILE 環境変数"
                fi
                
                if grep -z "RMW_IMPLEMENTATION=rmw_fastrtps_cpp" "$env_file" >/dev/null 2>&1; then
                    print_success "$node RMW 正しい結果を達成する"
                else
                    print_error "$node RMW 不適切な実装"
                fi
            fi
        fi
    done
    
    # 4. 共有メモリ転送を確認する
    print_info "共有メモリ転送を確認する..."
    local shm_files=$(ls /dev/shm/ 2>/dev/null | grep -E "(fastrtps|fast_dds|rmw)" | wc -l)
    if [ "$shm_files" -gt 0 ]; then
        print_success "共有メモリ転送が有効です ($shm_files ファイル)"
    else
        print_error "共有メモリ転送は検出されませんでした"
    fi
    
    # 5. DDSのテストによりパフォーマンスが明らかになった
    print_info "DDSのテストによりパフォーマンスが明らかになった..."
    local start_time=$(date +%s%3N)
    ros2 node list >/dev/null 2>&1
    local end_time=$(date +%s%3N)
    local discovery_time=$((end_time - start_time))
    
    if [ "$discovery_time" -lt 500 ]; then
        print_success "DDS 発見の遅延: ${discovery_time}ms (素晴らしい)"
    elif [ "$discovery_time" -lt 1000 ]; then
        print_info "DDS 発見の遅延: ${discovery_time}ms (良好)"
    else
        print_error "DDS 発見の遅延: ${discovery_time}ms (もっとゆっくり)"
    fi
}

# スクリプトディレクトリに切り替える
cd "$(dirname "$0")"
cd ..

# DDS構成ファイルを構成する
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export RMW_FASTRTPS_USE_QOS_FROM_XML=1
export FASTRTPS_DEFAULT_PROFILES_FILE="$(pwd)/assets/rt_fastdds_profile.xml"
print_info "DDS構成ファイルを構成する: $FASTRTPS_DEFAULT_PROFILES_FILE"

# DDS構成ファイルが存在するかどうかを確認してください。
if [ ! -f "$FASTRTPS_DEFAULT_PROFILES_FILE" ]; then
    print_error "DDS設定ファイルが存在しません。: $FASTRTPS_DEFAULT_PROFILES_FILE"
    exit 1
fi

# セットアップファイルが読み込まれているかどうかを確認してください。
if [ -z "$AMENT_PREFIX_PATH" ]; then
    print_info "ROS 2環境が検出されませんでした。ソースを実行します。..."
    source /opt/ros/humble/setup.bash || {
        print_error "できません。source /opt/ros/humble/setup.bash，パスが正しいかどうか確認してください。"
        exit 1
    }
fi

# colconとros2をチェックしてください
if ! command -v colcon &> /dev/null; then
    print_error "Colconがインストールされていません。ROS 2開発ツールをインストールしてください。"
    exit 1
fi
if ! command -v ros2 &> /dev/null; then
    print_error "ROS2がインストールされていません"
    exit 1
fi

# screenインストール確認
if ! command -v screen &> /dev/null; then
    print_error "screenがインストールされていません"
    exit 1
fi

# 推論パッケージをコンパイルする
print_info "推論パッケージをコンパイルする..."
colcon build --symlink-install || {
    print_error "推論パッケージのコンパイルに失敗しました"
    exit 1
}
source install/setup.bash

# 実行中のスクリーンセッションをすべて停止してください。
print_info "既存の関連スクリーンセッションを停止します..."
cleanup_sessions

start_component "inference_session" "ros2 launch inference inference.launch.py" "inference_node" 5
start_component "joy_session" "ros2 run joy joy_node" "joy_node" 2

# 検証ノードのDDS構成
verify_dds_effectiveness

# すべてのコンポーネントが起動しました。
print_success "----------------------------------------"
print_success "すべてのコンポーネントがバックグラウンドで正常に起動しました！"
print_success "各コンポーネントの出力を表示するには、次のコマンドを使用します。"
print_success "推論モジュール: screen -r inference_session"
print_success "コントローラ制御: screen -r joy_session"
print_success "----------------------------------------"
print_info "スクリーンセッションを終了するには、Ctrl+Aを押してからDを押します。"
print_info "以下のコマンドを使用して、すべてのコンポーネントを停止します。"
print_info "screen -S inference_session -X quit"
print_info "screen -S joy_session -X quit"
print_success "----------------------------------------"
print_info "コントローラ操作手順:"
print_info "Xボタン: モーターの有効化/無効化"
print_info "Aボタン: モーターをリセット"
print_info "Bボタン: 推論の開始/一時停止"
print_info "Yボタン: ゲームパッド操作とcmd_velコマンド操作を切り替える"
print_info "LBボタン: ポリシーモードを切り替える（beyond mimic有／割り込みモードで利用可能）"
print_info "RBボタン: 動作シーケンスを切り替える（beyondMimicモードで利用可能）"
print_info "右摇杆: 前進、後退、左折、右折を制御する"
print_info "LT/RT: ステアリング操作（左右回転）"
