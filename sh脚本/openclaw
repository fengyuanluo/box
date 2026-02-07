#!/usr/bin/env bash

# OpenClaw 一体化运维脚本
# 功能：Gateway/Node 安装、启停、重启、状态、日志、节点配对、模型管理

set -euo pipefail

SCRIPT_NAME="$(basename "$0")"
DEFAULT_GATEWAY_PORT=18789
DEFAULT_GATEWAY_HOST="127.0.0.1"
DEFAULT_GATEWAY_RUNTIME="node"
DEFAULT_NODE_RUNTIME="node"
DEFAULT_NODE_DISPLAY_NAME="Local Node"
DEFAULT_LOG_LINES=200

DRY_RUN=0
VERBOSE=0
ASSUME_YES=0
OPENCLAW_BIN="${OPENCLAW_BIN:-openclaw}"

if [[ -t 1 ]]; then
  C_RESET='\033[0m'
  C_INFO='\033[36m'
  C_WARN='\033[33m'
  C_ERR='\033[31m'
  C_OK='\033[32m'
  C_CMD='\033[35m'
else
  C_RESET=''
  C_INFO=''
  C_WARN=''
  C_ERR=''
  C_OK=''
  C_CMD=''
fi

info() { echo -e "${C_INFO}[INFO]${C_RESET} $*"; }
warn() { echo -e "${C_WARN}[WARN]${C_RESET} $*"; }
success() { echo -e "${C_OK}[OK]${C_RESET} $*"; }
error() { echo -e "${C_ERR}[ERROR]${C_RESET} $*" >&2; }

die() {
  error "$*"
  exit 1
}

print_cmd() {
  echo -e "${C_CMD}+ $*${C_RESET}"
}

run() {
  if ((DRY_RUN)); then
    print_cmd "$*"
    return 0
  fi
  if ((VERBOSE)); then
    print_cmd "$*"
  fi
  "$@"
}

run_shell() {
  local command="$1"
  if ((DRY_RUN)); then
    print_cmd "bash -lc $command"
    return 0
  fi
  if ((VERBOSE)); then
    print_cmd "bash -lc $command"
  fi
  bash -lc "$command"
}

trim() {
  local value="$1"
  value="${value#${value%%[![:space:]]*}}"
  value="${value%${value##*[![:space:]]}}"
  printf "%s" "$value"
}

quote_args() {
  local out=""
  local arg=""
  for arg in "$@"; do
    printf -v arg '%q' "$arg"
    out+="$arg "
  done
  out="${out% }"
  printf "%s" "$out"
}

need_cmd() {
  local cmd="$1"
  command -v "$cmd" >/dev/null 2>&1 || die "缺少命令：$cmd"
}

have_cmd() {
  command -v "$1" >/dev/null 2>&1
}

ensure_openclaw() {
  if have_cmd "$OPENCLAW_BIN"; then
    return 0
  fi
  if ((DRY_RUN)); then
    warn "dry-run: 未检测到 $OPENCLAW_BIN，后续仅打印命令。"
    return 0
  fi
  die "未找到 $OPENCLAW_BIN。请先执行 '$SCRIPT_NAME install openclaw'。"
}

oc() {
  ensure_openclaw
  run "$OPENCLAW_BIN" "$@"
}

oc_capture() {
  ensure_openclaw
  "$OPENCLAW_BIN" "$@"
}

config_get_or_empty() {
  local path="$1"
  if ((DRY_RUN)); then
    echo ""
    return 0
  fi
  local output=""
  if output="$(oc_capture config get "$path" 2>/dev/null)"; then
    trim "$output"
    return 0
  fi
  echo ""
}

confirm() {
  local prompt="$1"
  if ((ASSUME_YES)); then
    return 0
  fi
  local reply=""
  read -r -p "$prompt [y/N]: " reply
  [[ "$reply" == "y" || "$reply" == "Y" ]]
}

generate_token() {
  head -c 24 /dev/urandom | base64 | tr -d '=+/' | cut -c1-32
}

gateway_profile_suffix() {
  local profile="${OPENCLAW_PROFILE:-}"
  profile="$(trim "$profile")"
  if [[ -z "$profile" || "$profile" == "default" ]]; then
    echo ""
  else
    echo "-$profile"
  fi
}

gateway_unit_name() {
  echo "openclaw-gateway$(gateway_profile_suffix)"
}

node_unit_name() {
  echo "openclaw-node"
}

show_usage() {
  cat <<'USAGE'
OpenClaw 一体化运维脚本

用法:
  openclaw-ops.sh [全局参数] <命令> [子命令] [参数]

全局参数:
  --dry-run            仅打印命令，不执行
  --verbose            打印执行细节
  --yes, -y            跳过确认
  --openclaw-bin PATH  指定 openclaw 可执行文件（默认: openclaw）
  --help, -h           查看帮助

核心命令:
  init local-stack     初始化本机 Gateway + 本机 Node（默认推荐）
  install ...          安装 OpenClaw / Gateway 服务 / Node 服务
  gateway ...          Gateway 启停/重启/状态/日志
  node ...             Node 启停/重启/状态/日志/前台运行
  pairing ...          节点配对（pending/approve/reject/list/status）
  models ...           模型管理（list/status/set/provider/auth/probe）
  check health         一键健康检查

示例:
  ./scripts/openclaw-ops.sh init local-stack
  ./scripts/openclaw-ops.sh gateway status
  ./scripts/openclaw-ops.sh node logs --follow
  ./scripts/openclaw-ops.sh pairing pending
  ./scripts/openclaw-ops.sh models add-provider --provider moonshot --base-url https://api.moonshot.ai/v1 --api-key-env MOONSHOT_API_KEY --api openai-completions --model kimi-k2.5 --set-default
USAGE
}

show_install_usage() {
  cat <<'USAGE'
安装命令:
  install openclaw [--method installer|npm|skip] [--version latest] [--beta] [--onboard]
  install gateway [--port N] [--runtime node|bun] [--token TOKEN] [--force]
  install node [--host HOST] [--port N] [--display-name NAME] [--runtime node|bun] [--tls] [--tls-fingerprint SHA] [--force]
  install all [同 init local-stack 参数]
USAGE
}

show_init_usage() {
  cat <<'USAGE'
初始化命令:
  init local-stack [参数]

参数:
  --install-method installer|npm|skip   OpenClaw 安装方式（默认 installer）
  --version VERSION                     npm 版本（默认 latest）
  --beta                                使用 beta 渠道（仅 installer）
  --gateway-port N                      Gateway 端口（默认 18789）
  --gateway-token TOKEN                 指定 gateway.auth.token
  --gateway-runtime node|bun            Gateway 服务 runtime（默认 node）
  --node-runtime node|bun               Node 服务 runtime（默认 node）
  --node-host HOST                      Node 连接 Gateway 的 host（默认 127.0.0.1）
  --node-display-name NAME              Node 显示名（默认 Local Node）
  --node-tls                            Node 连接使用 TLS
  --node-tls-fingerprint SHA256         Node TLS 指纹
  --force                               重装服务
USAGE
}

show_gateway_usage() {
  cat <<'USAGE'
Gateway 命令:
  gateway install [--port N] [--runtime node|bun] [--token TOKEN] [--force]
  gateway start
  gateway stop
  gateway restart
  gateway status [--deep] [--json]
  gateway logs [--follow] [--lines N] [--source auto|journal|cli]
  gateway run [透传给 openclaw gateway run 的参数]
USAGE
}

show_node_usage() {
  cat <<'USAGE'
Node 命令:
  node install [--host HOST] [--port N] [--display-name NAME] [--runtime node|bun] [--tls] [--tls-fingerprint SHA] [--force]
  node start
  node stop
  node restart
  node status [--json]
  node uninstall
  node logs [--follow] [--lines N]
  node run-foreground [--host HOST] [--port N] [--display-name NAME] [--tls] [--tls-fingerprint SHA]
  node connect-remote --host HOST [--port N] [--display-name NAME] [--runtime node|bun] [--tls] [--tls-fingerprint SHA] [--force]
USAGE
}

show_pairing_usage() {
  cat <<'USAGE'
配对命令:
  pairing pending
  pairing list
  pairing approve <requestId>
  pairing reject <requestId>
  pairing status
USAGE
}

show_models_usage() {
  cat <<'USAGE'
模型命令:
  models status
  models list
  models set --model <provider/model 或 alias>
  models probe
  models add-provider --provider ID [--base-url URL] [--api openai-completions|anthropic-messages] [--api-key KEY | --api-key-env ENV] [--model MODEL_ID] [--name MODEL_NAME] [--set-default]
  models auth login --provider ID [--set-default]
  models auth setup-token --provider ID
  models auth paste-token --provider ID --token VALUE
USAGE
}

install_openclaw() {
  local method="$1"
  local version="$2"
  local use_beta="$3"
  local run_onboard="$4"

  case "$method" in
    skip)
      info "跳过 OpenClaw 安装。"
      ;;
    installer)
      need_cmd curl
      local flags=("--no-onboard")
      if [[ "$use_beta" == "1" ]]; then
        flags+=("--beta")
      fi
      if [[ "$version" != "latest" ]]; then
        flags+=("--version" "$version")
      fi
      local quoted
      quoted="$(quote_args "${flags[@]}")"
      run_shell "curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- $quoted"
      ;;
    npm)
      need_cmd npm
      local spec="openclaw@${version}"
      run env SHARP_IGNORE_GLOBAL_LIBVIPS=1 npm install -g "$spec"
      ;;
    *)
      die "不支持的安装方式: $method"
      ;;
  esac

  if [[ "$method" != "skip" ]]; then
    if have_cmd "$OPENCLAW_BIN"; then
      run "$OPENCLAW_BIN" doctor --non-interactive || true
    else
      warn "安装完成后暂未发现 $OPENCLAW_BIN，请检查 PATH。"
    fi
  fi

  if [[ "$run_onboard" == "1" ]]; then
    oc onboard --install-daemon
  fi
}

install_gateway_service() {
  local port="$1"
  local runtime="$2"
  local token="$3"
  local force="$4"

  local args=(gateway install --port "$port" --runtime "$runtime")
  if [[ -n "$token" ]]; then
    args+=(--token "$token")
  fi
  if [[ "$force" == "1" ]]; then
    args+=(--force)
  fi
  oc "${args[@]}"
}

install_node_service() {
  local host="$1"
  local port="$2"
  local display_name="$3"
  local runtime="$4"
  local tls="$5"
  local tls_fingerprint="$6"
  local force="$7"

  local args=(node install --host "$host" --port "$port" --runtime "$runtime")
  if [[ -n "$display_name" ]]; then
    args+=(--display-name "$display_name")
  fi
  if [[ "$tls" == "1" ]]; then
    args+=(--tls)
  fi
  if [[ -n "$tls_fingerprint" ]]; then
    args+=(--tls-fingerprint "$tls_fingerprint")
  fi
  if [[ "$force" == "1" ]]; then
    args+=(--force)
  fi
  oc "${args[@]}"
}

apply_local_defaults() {
  local gateway_port="$1"
  local gateway_token="$2"
  local node_display_name="$3"

  oc config set gateway.mode local
  oc config set gateway.bind loopback
  oc config set gateway.port "$gateway_port" --json

  if [[ -n "$gateway_token" ]]; then
    oc config set gateway.auth.mode token
    oc config set gateway.auth.token "$gateway_token"
  else
    local existing
    existing="$(config_get_or_empty gateway.auth.token)"
    if [[ -z "$existing" ]]; then
      local generated
      generated="$(generate_token)"
      oc config set gateway.auth.mode token
      oc config set gateway.auth.token "$generated"
      warn "未检测到 gateway.auth.token，已生成新 token: $generated"
    fi
  fi

  oc config set tools.exec.host node
  oc config set tools.exec.security allowlist
  if [[ -n "$node_display_name" ]]; then
    oc config set tools.exec.node "$node_display_name"
  fi
}

init_local_stack() {
  local install_method="$1"
  local version="$2"
  local use_beta="$3"
  local gateway_port="$4"
  local gateway_token="$5"
  local gateway_runtime="$6"
  local node_runtime="$7"
  local node_host="$8"
  local node_display_name="$9"
  local node_tls="${10}"
  local node_tls_fingerprint="${11}"
  local force="${12}"

  if ! have_cmd "$OPENCLAW_BIN"; then
    if [[ "$install_method" == "skip" ]]; then
      if ((DRY_RUN)); then
        warn "dry-run: 未检测到 $OPENCLAW_BIN，且 install-method=skip；仅输出计划命令。"
      else
        die "未检测到 $OPENCLAW_BIN，且 install-method=skip。"
      fi
    fi
    info "开始安装 OpenClaw（方式: $install_method）"
    install_openclaw "$install_method" "$version" "$use_beta" "0"
  else
    info "检测到 OpenClaw 已安装，跳过安装步骤。"
  fi

  ensure_openclaw
  apply_local_defaults "$gateway_port" "$gateway_token" "$node_display_name"

  info "安装/更新 Gateway 服务"
  install_gateway_service "$gateway_port" "$gateway_runtime" "$gateway_token" "$force"
  oc gateway restart

  info "安装/更新 Node 服务"
  install_node_service "$node_host" "$gateway_port" "$node_display_name" "$node_runtime" "$node_tls" "$node_tls_fingerprint" "$force"
  oc node restart

  success "本机 Gateway + Node 初始化完成。"
  info "建议执行以下命令确认配对和状态："
  echo "  $OPENCLAW_BIN nodes pending"
  echo "  $OPENCLAW_BIN nodes approve <requestId>"
  echo "  $OPENCLAW_BIN nodes status --connected"
  echo "  $OPENCLAW_BIN gateway status"
}

show_gateway_logs() {
  local follow="$1"
  local lines="$2"
  local source="$3"

  local unit
  unit="$(gateway_unit_name)"

  if [[ "$source" == "auto" || "$source" == "journal" ]]; then
    if have_cmd journalctl; then
      local args=(--user -u "${unit}.service" -n "$lines" --no-pager)
      if [[ "$follow" == "1" ]]; then
        args+=(-f)
      fi
      if run journalctl "${args[@]}"; then
        return 0
      fi
      [[ "$source" == "journal" ]] && die "journalctl 查看 Gateway 日志失败。"
      warn "journalctl 日志读取失败，回退到 openclaw logs。"
    elif [[ "$source" == "journal" ]]; then
      die "当前系统未安装 journalctl。"
    fi
  fi

  local args=(logs)
  if [[ "$follow" == "1" ]]; then
    args+=(--follow)
  fi
  oc "${args[@]}"
}

show_node_logs() {
  local follow="$1"
  local lines="$2"
  local unit
  unit="$(node_unit_name)"

  have_cmd journalctl || die "当前系统未安装 journalctl，无法查看 node systemd 日志。"
  local args=(--user -u "${unit}.service" -n "$lines" --no-pager)
  if [[ "$follow" == "1" ]]; then
    args+=(-f)
  fi
  run journalctl "${args[@]}"
}

cmd_install() {
  local target="${1:-}"
  [[ -z "$target" ]] && { show_install_usage; return 0; }
  shift || true

  case "$target" in
    openclaw)
      local method="installer"
      local version="latest"
      local use_beta="0"
      local onboard="0"
      while (($#)); do
        case "$1" in
          --method)
            shift; method="${1:-}" ;;
          --version)
            shift; version="${1:-}" ;;
          --beta)
            use_beta="1" ;;
          --onboard)
            onboard="1" ;;
          --help|-h)
            show_install_usage; return 0 ;;
          *)
            die "install openclaw: 未知参数 $1" ;;
        esac
        shift || true
      done
      install_openclaw "$method" "$version" "$use_beta" "$onboard"
      ;;

    gateway)
      ensure_openclaw
      local port="$DEFAULT_GATEWAY_PORT"
      local runtime="$DEFAULT_GATEWAY_RUNTIME"
      local token=""
      local force="0"
      while (($#)); do
        case "$1" in
          --port)
            shift; port="${1:-}" ;;
          --runtime)
            shift; runtime="${1:-}" ;;
          --token)
            shift; token="${1:-}" ;;
          --force)
            force="1" ;;
          --help|-h)
            show_gateway_usage; return 0 ;;
          *)
            die "install gateway: 未知参数 $1" ;;
        esac
        shift || true
      done
      install_gateway_service "$port" "$runtime" "$token" "$force"
      ;;

    node)
      ensure_openclaw
      local host="$DEFAULT_GATEWAY_HOST"
      local port="$DEFAULT_GATEWAY_PORT"
      local display_name="$DEFAULT_NODE_DISPLAY_NAME"
      local runtime="$DEFAULT_NODE_RUNTIME"
      local tls="0"
      local tls_fingerprint=""
      local force="0"
      while (($#)); do
        case "$1" in
          --host)
            shift; host="${1:-}" ;;
          --port)
            shift; port="${1:-}" ;;
          --display-name)
            shift; display_name="${1:-}" ;;
          --runtime)
            shift; runtime="${1:-}" ;;
          --tls)
            tls="1" ;;
          --tls-fingerprint)
            shift; tls_fingerprint="${1:-}" ;;
          --force)
            force="1" ;;
          --help|-h)
            show_node_usage; return 0 ;;
          *)
            die "install node: 未知参数 $1" ;;
        esac
        shift || true
      done
      install_node_service "$host" "$port" "$display_name" "$runtime" "$tls" "$tls_fingerprint" "$force"
      ;;

    all)
      cmd_init local-stack "$@"
      ;;

    *)
      die "install: 不支持的目标 $target"
      ;;
  esac
}

cmd_init() {
  local target="${1:-}"
  [[ -z "$target" ]] && { show_init_usage; return 0; }
  shift || true

  case "$target" in
    local-stack)
      local install_method="installer"
      local version="latest"
      local use_beta="0"
      local gateway_port="$DEFAULT_GATEWAY_PORT"
      local gateway_token=""
      local gateway_runtime="$DEFAULT_GATEWAY_RUNTIME"
      local node_runtime="$DEFAULT_NODE_RUNTIME"
      local node_host="$DEFAULT_GATEWAY_HOST"
      local node_display_name="$DEFAULT_NODE_DISPLAY_NAME"
      local node_tls="0"
      local node_tls_fingerprint=""
      local force="0"

      while (($#)); do
        case "$1" in
          --install-method)
            shift; install_method="${1:-}" ;;
          --version)
            shift; version="${1:-}" ;;
          --beta)
            use_beta="1" ;;
          --gateway-port)
            shift; gateway_port="${1:-}" ;;
          --gateway-token)
            shift; gateway_token="${1:-}" ;;
          --gateway-runtime)
            shift; gateway_runtime="${1:-}" ;;
          --node-runtime)
            shift; node_runtime="${1:-}" ;;
          --node-host)
            shift; node_host="${1:-}" ;;
          --node-display-name)
            shift; node_display_name="${1:-}" ;;
          --node-tls)
            node_tls="1" ;;
          --node-tls-fingerprint)
            shift; node_tls_fingerprint="${1:-}" ;;
          --force)
            force="1" ;;
          --help|-h)
            show_init_usage; return 0 ;;
          *)
            die "init local-stack: 未知参数 $1" ;;
        esac
        shift || true
      done

      case "$install_method" in
        installer|npm|skip) ;;
        *) die "--install-method 仅支持 installer|npm|skip" ;;
      esac

      init_local_stack "$install_method" "$version" "$use_beta" "$gateway_port" "$gateway_token" "$gateway_runtime" "$node_runtime" "$node_host" "$node_display_name" "$node_tls" "$node_tls_fingerprint" "$force"
      ;;

    *)
      die "init: 不支持的目标 $target"
      ;;
  esac
}

cmd_gateway() {
  local action="${1:-}"
  [[ -z "$action" ]] && { show_gateway_usage; return 0; }
  shift || true

  case "$action" in
    install)
      ensure_openclaw
      cmd_install gateway "$@"
      ;;
    start)
      ensure_openclaw
      oc gateway start "$@"
      ;;
    stop)
      ensure_openclaw
      oc gateway stop "$@"
      ;;
    restart)
      ensure_openclaw
      oc gateway restart "$@"
      ;;
    status)
      ensure_openclaw
      oc gateway status "$@"
      ;;
    run)
      ensure_openclaw
      oc gateway run "$@"
      ;;
    logs)
      local follow="0"
      local lines="$DEFAULT_LOG_LINES"
      local source="auto"
      while (($#)); do
        case "$1" in
          --follow|-f)
            follow="1" ;;
          --lines)
            shift; lines="${1:-}" ;;
          --source)
            shift; source="${1:-}" ;;
          --help|-h)
            show_gateway_usage; return 0 ;;
          *)
            die "gateway logs: 未知参数 $1" ;;
        esac
        shift || true
      done
      case "$source" in
        auto|journal|cli) ;;
        *) die "gateway logs --source 仅支持 auto|journal|cli" ;;
      esac
      ensure_openclaw
      show_gateway_logs "$follow" "$lines" "$source"
      ;;
    *)
      die "gateway: 不支持的操作 $action"
      ;;
  esac
}

cmd_node() {
  local action="${1:-}"
  [[ -z "$action" ]] && { show_node_usage; return 0; }
  shift || true

  case "$action" in
    install)
      ensure_openclaw
      cmd_install node "$@"
      ;;
    start)
      ensure_openclaw
      oc node restart "$@"
      ;;
    stop)
      ensure_openclaw
      oc node stop "$@"
      ;;
    restart)
      ensure_openclaw
      oc node restart "$@"
      ;;
    status)
      ensure_openclaw
      oc node status "$@"
      ;;
    uninstall)
      ensure_openclaw
      oc node uninstall "$@"
      ;;
    logs)
      local follow="0"
      local lines="$DEFAULT_LOG_LINES"
      while (($#)); do
        case "$1" in
          --follow|-f)
            follow="1" ;;
          --lines)
            shift; lines="${1:-}" ;;
          --help|-h)
            show_node_usage; return 0 ;;
          *)
            die "node logs: 未知参数 $1" ;;
        esac
        shift || true
      done
      ensure_openclaw
      show_node_logs "$follow" "$lines"
      ;;
    run-foreground)
      local host="$DEFAULT_GATEWAY_HOST"
      local port="$DEFAULT_GATEWAY_PORT"
      local display_name=""
      local tls="0"
      local tls_fingerprint=""
      while (($#)); do
        case "$1" in
          --host)
            shift; host="${1:-}" ;;
          --port)
            shift; port="${1:-}" ;;
          --display-name)
            shift; display_name="${1:-}" ;;
          --tls)
            tls="1" ;;
          --tls-fingerprint)
            shift; tls_fingerprint="${1:-}" ;;
          --help|-h)
            show_node_usage; return 0 ;;
          *)
            die "node run-foreground: 未知参数 $1" ;;
        esac
        shift || true
      done
      ensure_openclaw
      local args=(node run --host "$host" --port "$port")
      if [[ -n "$display_name" ]]; then
        args+=(--display-name "$display_name")
      fi
      if [[ "$tls" == "1" ]]; then
        args+=(--tls)
      fi
      if [[ -n "$tls_fingerprint" ]]; then
        args+=(--tls-fingerprint "$tls_fingerprint")
      fi
      oc "${args[@]}"
      ;;
    connect-remote)
      local host=""
      local port="$DEFAULT_GATEWAY_PORT"
      local display_name="$DEFAULT_NODE_DISPLAY_NAME"
      local runtime="$DEFAULT_NODE_RUNTIME"
      local tls="0"
      local tls_fingerprint=""
      local force="0"
      while (($#)); do
        case "$1" in
          --host)
            shift; host="${1:-}" ;;
          --port)
            shift; port="${1:-}" ;;
          --display-name)
            shift; display_name="${1:-}" ;;
          --runtime)
            shift; runtime="${1:-}" ;;
          --tls)
            tls="1" ;;
          --tls-fingerprint)
            shift; tls_fingerprint="${1:-}" ;;
          --force)
            force="1" ;;
          --help|-h)
            show_node_usage; return 0 ;;
          *)
            die "node connect-remote: 未知参数 $1" ;;
        esac
        shift || true
      done
      [[ -z "$host" ]] && die "node connect-remote 需要 --host"
      ensure_openclaw
      install_node_service "$host" "$port" "$display_name" "$runtime" "$tls" "$tls_fingerprint" "$force"
      oc node restart
      success "远程 Node 连接配置完成。"
      info "请在 Gateway 机器执行: $OPENCLAW_BIN nodes pending / approve"
      ;;
    *)
      die "node: 不支持的操作 $action"
      ;;
  esac
}

cmd_pairing() {
  local action="${1:-}"
  [[ -z "$action" ]] && { show_pairing_usage; return 0; }
  shift || true

  case "$action" in
    pending)
      ensure_openclaw
      oc nodes pending "$@"
      ;;
    list)
      ensure_openclaw
      oc nodes list "$@"
      ;;
    approve)
      local request_id="${1:-}"
      [[ -z "$request_id" ]] && die "pairing approve 需要 requestId"
      shift || true
      ensure_openclaw
      oc nodes approve "$request_id" "$@"
      ;;
    reject)
      local request_id="${1:-}"
      [[ -z "$request_id" ]] && die "pairing reject 需要 requestId"
      shift || true
      ensure_openclaw
      oc nodes reject "$request_id" "$@"
      ;;
    status)
      ensure_openclaw
      oc nodes status "$@"
      ;;
    *)
      die "pairing: 不支持的操作 $action"
      ;;
  esac
}

models_add_provider() {
  local provider="$1"
  local base_url="$2"
  local api="$3"
  local api_key="$4"
  local api_key_env="$5"
  local model_id="$6"
  local model_name="$7"
  local set_default="$8"

  [[ -z "$provider" ]] && die "models add-provider 需要 --provider"
  if [[ -n "$api_key" && -n "$api_key_env" ]]; then
    die "--api-key 与 --api-key-env 只能二选一"
  fi

  oc config set models.mode merge

  if [[ -n "$base_url" ]]; then
    oc config set "models.providers.${provider}.baseUrl" "$base_url"
  fi
  if [[ -n "$api" ]]; then
    oc config set "models.providers.${provider}.api" "$api"
  fi
  if [[ -n "$api_key" ]]; then
    oc config set "models.providers.${provider}.apiKey" "$api_key"
  fi
  if [[ -n "$api_key_env" ]]; then
    oc config set "models.providers.${provider}.apiKey" "\${${api_key_env}}"
  fi
  if [[ -n "$model_id" ]]; then
    oc config set "models.providers.${provider}.models[0].id" "$model_id"
    if [[ -n "$model_name" ]]; then
      oc config set "models.providers.${provider}.models[0].name" "$model_name"
    fi
  fi

  if [[ "$set_default" == "1" ]]; then
    [[ -z "$model_id" ]] && die "--set-default 需要同时指定 --model"
    oc models set "${provider}/${model_id}"
  fi

  success "Provider 配置完成：$provider"
  info "可用以下命令验证："
  echo "  $OPENCLAW_BIN models list"
  echo "  $OPENCLAW_BIN models status"
}

cmd_models_auth() {
  local action="${1:-}"
  [[ -z "$action" ]] && die "models auth 需要子命令（login/setup-token/paste-token）"
  shift || true

  case "$action" in
    login)
      local provider=""
      local set_default="0"
      while (($#)); do
        case "$1" in
          --provider)
            shift; provider="${1:-}" ;;
          --set-default)
            set_default="1" ;;
          *)
            die "models auth login: 未知参数 $1" ;;
        esac
        shift || true
      done
      [[ -z "$provider" ]] && die "models auth login 需要 --provider"
      local args=(models auth login --provider "$provider")
      if [[ "$set_default" == "1" ]]; then
        args+=(--set-default)
      fi
      oc "${args[@]}"
      ;;

    setup-token)
      local provider=""
      while (($#)); do
        case "$1" in
          --provider)
            shift; provider="${1:-}" ;;
          *)
            die "models auth setup-token: 未知参数 $1" ;;
        esac
        shift || true
      done
      [[ -z "$provider" ]] && die "models auth setup-token 需要 --provider"
      oc models auth setup-token --provider "$provider"
      ;;

    paste-token)
      local provider=""
      local token=""
      while (($#)); do
        case "$1" in
          --provider)
            shift; provider="${1:-}" ;;
          --token)
            shift; token="${1:-}" ;;
          *)
            die "models auth paste-token: 未知参数 $1" ;;
        esac
        shift || true
      done
      [[ -z "$provider" ]] && die "models auth paste-token 需要 --provider"
      [[ -z "$token" ]] && die "models auth paste-token 需要 --token"
      oc models auth paste-token --provider "$provider" --token "$token"
      ;;

    *)
      die "models auth: 不支持的操作 $action"
      ;;
  esac
}

cmd_models() {
  local action="${1:-}"
  [[ -z "$action" ]] && { show_models_usage; return 0; }
  shift || true

  case "$action" in
    status)
      ensure_openclaw
      oc models status "$@"
      ;;
    list)
      ensure_openclaw
      oc models list "$@"
      ;;
    set)
      local model_ref=""
      while (($#)); do
        case "$1" in
          --model)
            shift; model_ref="${1:-}" ;;
          --help|-h)
            show_models_usage; return 0 ;;
          *)
            die "models set: 未知参数 $1（请使用 --model）" ;;
        esac
        shift || true
      done
      [[ -z "$model_ref" ]] && die "models set 需要 --model"
      ensure_openclaw
      oc models set "$model_ref"
      ;;
    probe)
      ensure_openclaw
      oc models status --probe "$@"
      ;;
    add-provider|add)
      local provider=""
      local base_url=""
      local api=""
      local api_key=""
      local api_key_env=""
      local model_id=""
      local model_name=""
      local set_default="0"
      while (($#)); do
        case "$1" in
          --provider)
            shift; provider="${1:-}" ;;
          --base-url)
            shift; base_url="${1:-}" ;;
          --api)
            shift; api="${1:-}" ;;
          --api-key)
            shift; api_key="${1:-}" ;;
          --api-key-env)
            shift; api_key_env="${1:-}" ;;
          --model)
            shift; model_id="${1:-}" ;;
          --name)
            shift; model_name="${1:-}" ;;
          --set-default)
            set_default="1" ;;
          --help|-h)
            show_models_usage; return 0 ;;
          *)
            die "models add-provider: 未知参数 $1" ;;
        esac
        shift || true
      done
      ensure_openclaw
      models_add_provider "$provider" "$base_url" "$api" "$api_key" "$api_key_env" "$model_id" "$model_name" "$set_default"
      ;;
    auth)
      ensure_openclaw
      cmd_models_auth "$@"
      ;;
    *)
      die "models: 不支持的操作 $action"
      ;;
  esac
}

cmd_check() {
  local action="${1:-}"
  [[ -z "$action" ]] && { echo "用法: check health"; return 0; }
  shift || true

  case "$action" in
    health)
      ensure_openclaw
      local failures=0

      info "检查 Gateway 服务状态..."
      if ! oc gateway status; then
        failures=$((failures + 1))
      fi

      info "检查 Gateway RPC 健康..."
      if ! oc gateway health; then
        failures=$((failures + 1))
      fi

      info "检查 Node 连接状态..."
      if ! oc nodes status --connected; then
        failures=$((failures + 1))
      fi

      info "检查模型状态..."
      if ! oc models status; then
        failures=$((failures + 1))
      fi

      if ((failures > 0)); then
        die "健康检查未通过，失败项数量: $failures"
      fi
      success "健康检查通过。"
      ;;
    *)
      die "check: 不支持的操作 $action"
      ;;
  esac
}

parse_global_flags() {
  local args=()
  while (($#)); do
    case "$1" in
      --dry-run)
        DRY_RUN=1
        ;;
      --verbose)
        VERBOSE=1
        ;;
      --yes|-y)
        ASSUME_YES=1
        ;;
      --openclaw-bin)
        shift
        OPENCLAW_BIN="${1:-}"
        [[ -n "$OPENCLAW_BIN" ]] || die "--openclaw-bin 需要参数"
        ;;
      --help|-h)
        show_usage
        exit 0
        ;;
      --)
        shift
        while (($#)); do args+=("$1"); shift; done
        break
        ;;
      -*)
        die "未知全局参数: $1"
        ;;
      *)
        args+=("$1")
        shift
        while (($#)); do args+=("$1"); shift; done
        break
        ;;
    esac
    shift || true
  done

  if ((${#args[@]} == 0)); then
    show_usage
    exit 0
  fi

  set -- "${args[@]}"
  COMMAND="$1"
  shift || true
  REMAINING_ARGS=("$@")
}

main() {
  local COMMAND=""
  local REMAINING_ARGS=()

  parse_global_flags "$@"

  case "$COMMAND" in
    help)
      show_usage
      ;;
    init)
      cmd_init "${REMAINING_ARGS[@]}"
      ;;
    install)
      cmd_install "${REMAINING_ARGS[@]}"
      ;;
    gateway)
      cmd_gateway "${REMAINING_ARGS[@]}"
      ;;
    node)
      cmd_node "${REMAINING_ARGS[@]}"
      ;;
    pairing)
      cmd_pairing "${REMAINING_ARGS[@]}"
      ;;
    models)
      cmd_models "${REMAINING_ARGS[@]}"
      ;;
    check)
      cmd_check "${REMAINING_ARGS[@]}"
      ;;
    *)
      die "未知命令: $COMMAND（使用 --help 查看帮助）"
      ;;
  esac
}

main "$@"
