### ## 1단계: NCP 서버 생성 및 초기 설정 (Classic 환경 기준)

#### **1. 서버 생성 시작**

1.  **NCP 콘솔 > Services > Compute > Server** 메뉴로 이동합니다.
2.  **[+ 서버 생성]** 버튼을 클릭합니다.

#### **2. 서버 이미지 및 스펙 선택**

1.  **OS 이미지 선택**: **Ubuntu**, 버전 **22.04** 선택을 권장합니다.
2.  **서버 타입**: **Micro** 또는 **Compact** 등 작은 사양으로 시작합니다.
3.  **요금제**: 테스트 목적이므로 **시간 요금제**를 선택합니다.
4.  **서버 이름**: `yahoo-server` 와 같이 식별하기 쉬운 이름을 입력합니다.

#### **3. 인증키 생성 (비밀번호 확인용)**

1.  **[새로운 인증키 생성]**을 선택합니다.
2.  인증키 이름(예: `ncp-classic-key`)을 입력하고 **[인증키 생성 및 저장]**을 클릭합니다.
3.  생성된 `.pem` 파일은 **내 PC의 안전한 곳(예: `~/.ssh/` 폴더)**에 잘 보관합니다.
    *   **핵심 포인트**: 이 키는 SSH 접속용이 아니라, 아래 5단계에서 **관리자 비밀번호를 확인**하는 데 사용됩니다.

#### **4. 방화벽(ACG) 설정**

1.  서버 생성 과정에서 ACG를 설정합니다. 기본 ACG를 사용해도 되지만, 아래 규칙이 반드시 포함되어야 합니다.
2.  **[ACG 생성]** 버튼을 눌러 새 ACG를 만듭니다.
3.  **Inbound 규칙**에 아래 두 가지를 추가하고 **[적용]**합니다.
    *   **SSH 접속용**: `프로토콜: TCP`, `접근소스: 0.0.0.0/0`, `허용포트: 22`
    *   **API 서버용**: `프로토콜: TCP`, `접근소스: 0.0.0.0/0`, `허용포트: 8000`
        *   (보안을 위해 `접근소스`는 내 IP 주소를 입력하는 것이 더 안전합니다.)

#### **5. 서버 생성 및 정보 확인**

1.  최종 확인 후 **[서버 생성]** 버튼을 클릭합니다.
2.  서버가 생성되면 목록에서 서버를 선택하고 **Public IP(공인 IP)**를 확인하여 메모해 둡니다.

-----

### ## 2단계: 서버 접속 및 배포 환경 준비

#### **1. 관리자 비밀번호 확인 (가장 중요)**

1.  NCP 콘솔에서 방금 생성한 서버를 선택합니다.
2.  상단 메뉴에서 **[서버 관리 및 설정 변경] > [관리자 비밀번호 확인]**을 클릭합니다.
3.  팝업창이 뜨면 1-3 단계에서 저장한 **`.pem` 인증키 파일**을 끌어다 놓습니다.
4.  화면에 표시되는 **관리자(`root`) 비밀번호**를 복사하여 안전한 곳에 메모합니다.

#### **2. 서버 최초 접속 (root 계정 사용)**

1.  내 PC의 터미널을 열고 아래 명령어를 입력합니다. **`ubuntu`가 아닌 `root` 계정**을 사용합니다.
    ```bash
    ssh root@<서버의_공인_IP>
    ```
2.  `password:`를 물어보면, 위에서 복사한 **관리자 비밀번호**를 붙여넣고 Enter를 누릅니다. (화면에 입력이 표시되지 않는 것이 정상입니다.)

#### **3. Docker 설치**

1.  서버에 성공적으로 접속했다면, 아래 명령어를 순서대로 실행하여 Docker를 설치합니다.
    ```bash
    apt-get update
    apt-get install -y ca-certificates curl git
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    chmod a+r /etc/apt/keyrings/docker.asc
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    ```

-----

### ## 3단계: API 서버 배포 및 최종 실행

#### **1. 프로젝트 코드 가져오기**

1.  GitHub 저장소의 코드를 서버로 복제합니다.
    ```bash
    git clone https://github.com/nsj02/yahoo-finance-mcp.git
    ```
2.  프로젝트 폴더로 이동합니다.
    ```bash
    cd yahoo-finance-mcp
    ```

#### **2. Docker 이미지 빌드**

1.  `Dockerfile`을 이용해 API 서버의 이미지를 만듭니다. (이때 `Dockerfile`의 `uv pip install` 명령어에는 `--system` 옵션이 포함되어 있어야 합니다.)
    ```bash
    docker build -t yahoo-finance-api .
    ```

#### **3. Docker 컨테이너 실행**

1.  만들어진 이미지를 백그라운드에서 실행시켜 API 서버를 켭니다.
    ```bash
    docker run -d --restart always -p 8000:8000 --name my-api-container yahoo-finance-api
    ```

#### **4. 최종 확인**

1.  내 PC의 웹 브라우저를 열고 주소창에 아래 주소를 입력합니다.
    ```
    http://<서버의_공인_IP>:8000/docs
    ```
2.  FastAPI가 자동으로 생성한 API 문서 페이지가 나타나면, 모든 과정이 성공적으로 완료된 것입니다. 이제 이 공개 주소를 이용해 원하는 AI 서비스와 연동할 수 있습니다.

