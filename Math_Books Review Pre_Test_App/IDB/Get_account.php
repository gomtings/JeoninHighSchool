<?php
    /* DB 연결 정보 */
    $host = "localhost";
    $user = "solimatics";
    $pw = "dudrnr68*";
    $dbName = "solimatics";
    $conn = mysqli_connect($host, $user, $pw, $dbName);

    /* 결과 변수 초기화 */
    $Completion = false;
    $data = array();

    /* DB 연결 확인 */
    if($conn){ // 연결 성공
        /* DB SELECT */
        $stmt = $conn->prepare("SELECT name, admin FROM JeoninInfo");
        $stmt->execute();
        $result = $stmt->get_result();

        if($result->num_rows > 0) {
            $Completion = true;
            $data = $result->fetch_all(MYSQLI_ASSOC); // 모든 사용자 정보 가져오기
        }

        if($Completion == true) {
            $json = json_encode(array("result" => 'success', "msg" => 'data retrieved', "data" => $data));
        } else {
            $json = json_encode(array("result" => 'fail', "msg" => 'no data found'));
        }

        echo($json);
        mysqli_close($conn);
    } else { // 연결 실패
        $json = json_encode(array("result" => 'fail', "msg" => 'DB connection fail'));
        echo($json);
    }
?>