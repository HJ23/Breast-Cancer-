var sep = "";
var AsyncFBLoaded = false;
var AsyncGPlusLoaded = false;
var GPlusFirstTime = false;
var isLoggedIn = false;

var AuthStates = {
    google: null,
    facebook: null
}

window.fbAsyncInit = function() {
    FB.init({
        appId      : '158463040929354',
        cookie     : true,  // enable cookies to allow the server to access
        xfbml      : true,  // parse social plugins on this page
        version    : 'v2.5' // use version 2.0
    });

    checkLoginStatus();
};

function signinCallback(authResult) {
    if (!isLoggedIn && !AsyncGPlusLoaded) {
        AsyncGPlusLoaded = true;
        AuthStates.google = authResult;
        $('#gplus-login').removeClass('btn-disabled');
        $('#gplus-login-register').removeClass('btn-disabled');
    } else if (GPlusFirstTime) {
        AsyncGPlusLoaded = true;
        AuthStates.google = authResult;
        GoViaGPlus();
    }
}

function checkLoginStatus() {
    if (!isLoggedIn) {
        if (!AsyncFBLoaded) {
            FB.getLoginStatus(function(response) {
                AuthStates.facebook = response;
                AsyncFBLoaded = true;
                $('#facebook-login').removeClass('btn-disabled');
                $('#facebook-login-register').removeClass('btn-disabled');
            });
        }
    }
}

$(document).ready(function() {
    //check login cookie status
    $.ajax({
        type: "POST",
        url: sep + "includes/wsdl/WSDLLoginStatus.php",
        data: "a=1",
        dataType: 'json',
        success: function (msg) {
            isLoggedIn = msg.IsLoggedIn;
        }
    });

    $("#maths-search").autocomplete({
        source: sep + "includes/wsdl/WSDLSearch.php"
    });

    $("#login-form").submit(function (e) {
        e.preventDefault();
        var str = $("#login-form").serialize();
        Login(str);
    });

    $('#facebook-login').click(function (e) {
        GoViaFB();
    });

    $('#gplus-login').click(function (e) {
        GoViaGPlus();
    });
    $('#facebook-login-register').click(function (e) {
        GoViaFB();
    });

    $('#gplus-login-register').click(function (e) {
        GoViaGPlus();
    });
});

function SetSep(s) {
    sep = s;
}

function GoViaFB() {
    var isInFB = false;
    var userExistsInMQ = 0;

    if (AsyncFBLoaded) {
        if (AuthStates.facebook) {
            if (AuthStates.facebook.status === 'connected') {
                var fbuid = AuthStates.facebook.authResponse.userID;
                $.ajax({
                    type: "POST",
                    url: sep + "includes/wsdl/WSDLLoginStatus.php",
                    data: "a=2&uid=" + fbuid,
                    dataType: 'json',
                    success: function (msg) {
                        userExistsInMQ = msg.UserExist;
                        console.log("user exists in MQ (FB)?:" + userExistsInMQ)
                        if (userExistsInMQ) {
                            Login('fid=' + fbuid);
                        } else {
                            FB.api('/me', { locale: 'en_UK', fields: 'name, email' },function(response) {
                                RegisterInMQ("sid=2&name=" + response.name + '&email=' + response.email + '&id=' + response.id);
                            });
                        }
                        isInFB = true;
                    }
                });

            } else if (AuthStates.facebook.status === 'not_authorized') {
                  FB.login(function(response) {
                      if (response.authResponse) {
                          FB.api('/me', { locale: 'en_UK', fields: 'name, email' },function(response) {
                              RegisterInMQ("sid=2&name=" + response.name + '&email=' + response.email + '&id=' + response.id);
                          });
                      } else {
                      }
                  },
                      {scope:'email'});
            } else {
                //nothing, not logged into FB
                FB.login(function(response) {
                        if (response.authResponse) {
                            FB.api('/me', { locale: 'en_UK', fields: 'name, email' },function(response) {
                                RegisterInMQ("sid=2&name=" + response.name + '&email=' + response.email + '&id=' + response.id);
                            });
                        } else {
                        }
                    },
                    {scope:'email'});
            }
        }
    }

    return isInFB;
}

function GoViaGPlus() {
    var userExistsInMQ = 0;

    if (AsyncGPlusLoaded) {
        if (AuthStates.google) {
            if (AuthStates.google['error']) {
                GPlusFirstTime = true;
            } else if (AuthStates.google['access_token']) {
                //lets login then
                //but first check if registered
                var resp = null;
                $.ajax({
                    type: "GET",
                    url: "https://www.googleapis.com/oauth2/v2/userinfo",
                    data: "access_token=" + AuthStates.google.access_token,
                    dataType: 'json',
                    success: function (msg) {
                        resp = msg;
                        //but first check if registered
                        $.ajax({
                            type: "POST",
                            url: sep + "includes/wsdl/WSDLLoginStatus.php",
                            data: "a=3&uid=" + resp.id,
                            dataType: 'json',
                            success: function (msg) {
                                userExistsInMQ = msg.UserExist;
                                if (userExistsInMQ) {
                                    //login via userId from G+
                                    Login('gid=' + resp.id);
                                } else {
                                    RegisterInMQ("sid=3&name=" + resp.name + '&email=' + resp.email + '&id=' + resp.id);
                                }
                            }
                        });
                    }
                });
            }
        }
    }
}

function chooseAuthProvider() {
    var isInFB = false;

    if (AsyncFBLoaded && AsyncGPlusLoaded) {
        isInFB = GoViaFB();

        if (AuthStates.google && !isInFB) {
            GoViaGPlus();
        }
    }
}

function Login(str) {
    $.ajax({
        type: "POST",
        url: sep + "includes/wsdl/WSDLLogin.php",
        data: str,
        dataType: 'json',

        beforeSend: function (xhr, opts) {
            $("#span-user").empty();
        },
        success: function (msg) {
            if (msg.hasErrors == 1) {
                window.location.replace("http://math-quiz.co.uk/login.html?e=" + msg.errorCode);
            } else {
                $('#login-parent').trigger('click');
                $("#login-parent").hide();
                $("#span-user").append(msg.username);
                $("#login-parent-logged").show();
                $("#login-parent-logged").addClass("animated tada");
                $.cookie("maths_cookie", msg.cookie_id, { expires : parseInt(msg.expiry) });
                window.location.replace("http://math-quiz.co.uk/profile.html");
            }
        }
    });
}
function RegisterInMQ(str) {
    console.log(str);
    $.ajax({
        type: "POST",
        url: sep + "includes/wsdl/WSDLSocialRegister.php",
        data: str,
        dataType: 'json',

        success: function (msg) {
            if (msg.hasErrors == 1) {
                window.location.replace("http://math-quiz.co.uk/login.html?e=" + msg.errorCode);
            } else {
                //chooseAuthProvider();
                $('#login-parent').trigger('click');
                $("#login-parent").hide();
                $("#span-user").append(msg.username);
                $("#login-parent-logged").show();
                $("#login-parent-logged").addClass("animated tada");
                $.cookie("maths_cookie", msg.cookie_id, { expires : parseInt(msg.expiry) });
                window.location.replace("http://math-quiz.co.uk/profile.html");
            }
        }
    });
}

// Load the FB SDK asynchronously
(function(d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) return;
    js = d.createElement(s); js.id = id;
    js.src = "//connect.facebook.net/en_UK/sdk.js";
    fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));
