var local = false;

AWS.config.update({
    region: "us-east-2",
    identityPoolId: "us-east-2:946b7ec1-dda0-4ef9-9b2f-e05141fc25d0"
});
AWS.config.credentials = new AWS.CognitoIdentityCredentials({
    IdentityPoolId: "us-east-2:946b7ec1-dda0-4ef9-9b2f-e05141fc25d0"
});


// Create DynamoDB service object
var ddb = new AWS.DynamoDB({ apiVersion: "2012-08-10" });

//addLink("link","title","author")

 function addLink(link, title, author, callback) {

    var params = {
        ExpressionAttributeValues: {
            ":increment": { N: "1" }
        },
        Key: {
            ELEM: {
                S: "CURRENT_LINK_NUM"
            },
            ID: {
                N: "0"
            }
        },
        UpdateExpression: "SET CURRENT_NUM = CURRENT_NUM + :increment",
        TableName: "DCLP",
        ReturnValues: "UPDATED_OLD"
    };
     ddb.updateItem(params, function (err, data) {
        if (err) {
            console.log("error", err);
        }
        else {
            //console.log("CURRENT_EVENT_NUM UPDATED. OLD = ", data.Attributes.CURRENT_NUM.N);
            //console.log(data.Attributes);
            var linkNum = Number(data.Attributes.CURRENT_NUM.N) + 1;
            var params = {
                Item: {
                    ELEM: {
                        S: "LINK"
                    },
                    ID: {
                        N: linkNum + ""
                    },
                    COMP_URL: {
                        S: link + ""
                    },
                    TITLE: {
                        S: title + ""
                    },
                    AUTHOR: {
                        S: author + ""
                    },
                    CURRENT_COMMENT_NUM: {
                        N: "0"
                    }
                },
                TableName: "DCLP"
            };
             ddb.putItem(params, function (err, data) {
                if (err) {
                    console.log("error", err);
                }
                else{
                    callback();
                }
            });
        }
    });
}

function postComment(compositionID, commentorName, comment, callback) {
    var params = {
        ExpressionAttributeValues: {
            ":increment": { N: "1" }
        },
        Key: {
            ELEM: {
                S: "LINK"
            },
            ID: {
                N: compositionID + ""
            }
        },
        UpdateExpression: "SET CURRENT_COMMENT_NUM = CURRENT_COMMENT_NUM + :increment",
        TableName: "DCLP",
        ReturnValues: "UPDATED_OLD"
    };
    ddb.updateItem(params, function (err, data) {
        if (err) {
            console.log("error", err);
        }
        else {
            var commentNum = Number(data.Attributes.CURRENT_COMMENT_NUM.N) + 1;

            var params = {
                Item: {
                    ELEM: {
                        S: "COMMENT_ELEM"
                    },
                    ID: {
                        N: ((Number(compositionID) * 1000000) + commentNum) + ""
                    },
                    COMMENT_CONTENT: {
                        S: comment + ""
                    },
                    COMMENTOR_NAME: {
                        S: commentorName + ""
                    },
                    COMMENT_NUM: {
                        N: commentNum + ""
                    },
                    POST_DATE: {
                        N: Date.now() + ""
                    }
                },
                TableName: "DCLP"
            };
            ddb.putItem(params, function (err, data) {
                if (err) {
                    console.log("error", err);
                }
                else {
                    callback();
                }
            });

        }
    });
}


function getLinks(callback) {
    var params = {
        KeyConditionExpression: "ELEM = :val",
        ExpressionAttributeValues: {
            ":val": { S: "LINK" }
        },
        ProjectionExpression: "COMP_URL, ID, TITLE, AUTHOR",
        TableName: "DCLP"
    };

    ddb.query(params, function (err, data) {
        if (err) {
            console.log("error", err);
        } else {
            console.log("DATA", data);
            data.Items.reverse();
            callback(data.Items);
        }
    })
}

function getComments(compositionID, callback) {
    var params = {
        KeyConditionExpression: "ELEM = :val AND ID BETWEEN :compid AND :compidUpper",
        ExpressionAttributeValues: {
            ":val": { S: "COMMENT_ELEM" },
            ":compid": { N: (Number(compositionID) * 1000000) + "" },
            ":compidUpper": { N: ((Number(compositionID) + 1) * 1000000) + "" },
        },
        ProjectionExpression: "COMMENTOR_NAME, COMMENT_CONTENT, POST_DATE",
        TableName: "DCLP"
    };

    ddb.query(params, function (err, data) {
        if (err) {
            console.log("error", err);
        } else {
            console.log("DATA", data);
            //data.Items.sort((a,b) => Number(a.COMMENT_NUM.N) - Number(b.COMMENT_NUM.N))
            callback(data.Items);
        }
    })
}