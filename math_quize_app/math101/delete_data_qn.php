<?php
    /* DB 연결 정보*/
    $host = "localhost";
    $user = "tkddn4508";
    $pw = "gom20726!";
    $dbName = "tkddn4508";
    $conn = mysqli_connect($host, $user, $pw, $dbName);

    /* DB 연결 확인 */
    if($conn){ // 연결 성공
        /* DB SELECT*/
        $question = $_POST['question'];

        $stmt = $conn->prepare("DELETE FROM math101 WHERE question = ?");
        $stmt->bind_param("s", $question);
        $stmt->execute();

        if ($stmt -> affected_rows > 0) {
            $json = json_encode(array("result" => 'success', "msg" => 'success'));
        } else {
            $json = json_encode(array("result" => 'fail', "msg" => 'delete fail'));
        }
        echo($json);
        mysqli_close($conn);
    }else{ // 연결 실패 
        $json = json_encode(array("result" => 'fail', "msg" => 'login fail'));
        echo($json);
    }
?>