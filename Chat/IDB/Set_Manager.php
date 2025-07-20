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

        /* DB SELECT */
        $stmt = $conn->prepare("SELECT name, admin FROM JeoninInfo WHERE name = ?");
        $stmt->bind_param("s", $name);
        $stmt->execute();
        $result = $stmt->get_result();

        if($result->num_rows > 0) {
            $Completion = true;
            $row = $result->fetch_assoc(); // 사용자 정보 가져오기
            $name = $row['name'];
            $admin = $row['admin'];

            /* admin 값 변경 */
            $new_admin = $admin == 1 ? 0 : 1;
            $update_stmt = $conn->prepare("UPDATE JeoninInfo SET admin = ? WHERE name = ?");
            $update_stmt->bind_param("is", $new_admin, $name);
            $update_stmt->execute();
        }

        if($Completion == true) {
            $json = json_encode(array("result" => 'success', "msg" => 'admin value updated', "name" => $name, "admin" => $new_admin));
        } else {
            $json = json_encode(array("result" => 'fail', "msg" => 'invalid credentials', "name" => $name));
        }

        echo($json);
        mysqli_close($conn);
    } else { // 연결 실패
        $json = json_encode(array("result" => 'fail', "msg" => 'DB connection fail'));
        echo($json);
    }
?>