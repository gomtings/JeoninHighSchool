<?php
    /* DB 연결 정보*/
    $host = "localhost";
    $user = "tkddn4508";
    $pw = "gom20726!";
    $dbName = "tkddn4508";
    $conn = mysqli_connect($host, $user, $pw, $dbName);
    $Completion = false;
    /* DB 연결 확인 */
    if($conn){ // 연결 성공
        /* DB SELECT*/
        $student_name = "이상우";//$_POST['name'];
        $student_num = 20230001;//$_POST['student_name'];
        $error_count = "{error_count : 1}";//$_POST['error_count'];
        $MSG = "반갑습니다.";$_POST['MSG']; 
        $MSG_TF = 0;//$_POST['MSG_TF'];

        $stmt = $conn->prepare("SELECT COUNT(*) AS count FROM Student WHERE name = ? AND student_num = ?")
        if ($stmt === false) {
            echo "Error: " . $conn->error;
        } else {
            $stmt->bind_param("si", $name, $student_num);
            $stmt->execute();
            $result = $stmt->get_result();
            $row = mysqli_fetch_array($result);
            // ...
        }
        echo($json);
        mysqli_close($conn);
    }else{ // 연결 실패 
        $json = json_encode(array("result" => 'fail', "msg" => 'login fail'));
        echo($json);
    }
?>