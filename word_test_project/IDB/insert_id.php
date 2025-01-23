<?php
    /* DB 연결 정보 */
    $host = "localhost";
    $user = "solimatics";
    $pw = "dudrnr68*";
    $dbName = "solimatics";
    $conn = mysqli_connect($host, $user, $pw, $dbName);
    $Completion = false;

    /* DB 연결 확인 */
    if($conn){ // 연결 성공
        /* POST 데이터 확인 및 초기화 */
        $name = isset($_POST['name']) ? $_POST['name'] : '';
        $student_num = isset($_POST['stunum']) ? $_POST['stunum'] : '';

        /* DB SELECT */
        $stmt = $conn->prepare("SELECT COUNT(*) AS count FROM JeoninInfo WHERE name = ? AND student_num = ?");
        $stmt->bind_param("ss", $name, $student_num);
        $stmt->execute();
        $result = $stmt->get_result();
        $row = mysqli_fetch_array($result);

        if ($row['count'] == 0) {
            $stmt = $conn->prepare("INSERT INTO JeoninInfo (name, student_num) VALUES (?, ?)");
            $stmt->bind_param("ss", $name, $student_num);

            if($stmt->execute()){
                $Completion = true;
                $idx = mysqli_insert_id($conn);
            } else {
                $Completion = false;
            }
        }

        if($Completion == true){
            $json = json_encode(array("result" => 'success', "msg" => 'success', "name" => $name, "student_num" => $student_num, "idx" => $idx));
        } else {
            $json = json_encode(array("result" => 'fail', "msg" => 'Completion fail'));
        }

        echo($json);
        mysqli_close($conn);
    } else { // 연결 실패
        $json = json_encode(array("result" => 'fail', "msg" => 'login fail'));
        echo($json);
    }
?>