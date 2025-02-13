<?php
    /* DB 연결 정보 */
    $host = "localhost";
    $user = "solimatics";
    $pw = "dudrnr68*";
    $dbName = "solimatics";
    $conn = mysqli_connect($host, $user, $pw, $dbName);

    /* 결과 변수 초기화 */
    $Completion = false;
    $name = '';
    $admin = '';

    /* DB 연결 확인 */
    if($conn){ // 연결 성공
        /* POST 데이터 확인 및 공백 제거 */
        $name = isset($_POST['name']) ? $_POST['name'] : '';
        $student_num = isset($_POST['stunum']) ? $_POST['stunum'] : '';

        /* DB SELECT */
        $stmt = $conn->prepare("SELECT name, admin FROM JeoninInfo WHERE name = ? AND student_num = ?");
        $stmt->bind_param("ss", $name, $student_num);
        $stmt->execute();
        $result = $stmt->get_result();

        if($result->num_rows > 0) {
            $Completion = true;
            $row = $result->fetch_assoc(); // 사용자 정보 가져오기
            $name = $row['name'];
            $admin = $row['admin'];
        }

        if($Completion == true) {
            $json = json_encode(array("result" => 'success', "msg" => 'login success', "name" => $name, "admin" => $admin));
        } else {
            $json = json_encode(array("result" => 'fail', "msg" => 'invalid credentials',"name" => $name,"student_num" => $student_num));
        }

        echo($json);
        mysqli_close($conn);
    } else { // 연결 실패
        $json = json_encode(array("result" => 'fail', "msg" => 'DB connection fail'));
        echo($json);
    }
?>
