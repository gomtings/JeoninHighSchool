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
        $book_num = $_POST['book_num'];
        $question = $_POST['question']; 
        $c_answer = $_POST['c_answer'];
        $f_answer1 = $_POST['f_answer1']; 
        $f_answer2 = $_POST['f_answer2'];
        $f_answer3 = $_POST['f_answer3'];

        $stmt = $conn->prepare("SELECT COUNT(*) AS count FROM math101 WHERE book_num = ? AND question = ?");
        $stmt->bind_param("is", $book_num, $question);
        $stmt->execute();
        $result = $stmt->get_result();
        $row = mysqli_fetch_array($result);
        if ($row['count'] == 0) {
            $stmt = $conn->prepare("INSERT INTO math101 (book_num, question, c_answer, f_answer1, f_answer2, f_answer3) VALUES (?, ?, ?, ?, ?, ?)");
            $stmt->bind_param("isssss", 
                $book_num, 
                $question, 
                $c_answer, 
                $f_answer1, 
                $f_answer2, 
                $f_answer3
            );
            if($stmt->execute()){
                $Completion = true;
                $idx = mysqli_insert_id($conn);
            }else{
                $Completion = false;
            }
        }
        if($Completion == true){
            $json = json_encode(array("result" => 'success', "msg" => 'success', "book_num" => $book_num, "question" => $question, "c_answer" => $c_answer, "f_answer1" => $f_answer1, "f_answer2" => $f_answer2, "f_answer3" =>$f_answer3,"idx" =>$idx));
        }else{
            $json = json_encode(array("result" => 'fail', "msg" => 'Completion fail'));
        }
        echo($json);
        mysqli_close($conn);
    }else{ // 연결 실패 
        $json = json_encode(array("result" => 'fail', "msg" => 'login fail'));
        echo($json);
    }
?>