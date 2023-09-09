package appium.tests.message

import appium.comm.InitAppium
import appium.pages.*
import io.cucumber.java.After
import io.cucumber.java.Before
import io.cucumber.java.Scenario
import io.cucumber.java.en.*
import org.junit.Assert
import java.time.LocalTime
import java.time.format.DateTimeFormatter

class MessageStep {

    private val ori: InitAppium by lazy { InitAppium() }
    private lateinit var loginPage :LoginPage
    private lateinit var messagePage :MessagePage
    private lateinit var friendPage: FriendPage
    private lateinit var registerPage: RegisterPage
    private lateinit var commonPage : CommonPage

    @Before
    fun setUp() {
        ori.setUp().apply {
            loginPage = LoginPage(this)
            messagePage = MessagePage(this)
            friendPage = FriendPage(this)
            commonPage = CommonPage(this)
            registerPage = RegisterPage(this)
        }

    }

    @Given("M> Login with Account:{string}, Password:{string}, LoginType:{string}")
    @Throws(Exception::class)
    fun login(acc:String,pwd:String, loginType:String) {
        loginPage.reject()
        loginPage.toggleType(loginType)
        loginPage.inputAcc(acc)
        loginPage.inputPwd(pwd)
        loginPage.passAll()
        Assert.assertTrue(commonPage.checkTitle("好友"))
    }

    @Given("M> Register with Account:{string}, Password:{string}, Captcha: {string}, Nickname: {string}, Mail: {string}, MPlusId: {string}")
    @Throws(Exception::class)
    fun register(acc:String, pwd:String, captcha:String, nickname:String, mail:String, mPlusId:String) {
        registerPage.reject()
        registerPage.registerAcc(acc)
        registerPage.inputCaptcha(captcha)
        registerPage.inputNickname(nickname)
        commonPage.findMore()
        registerPage.inputId(mPlusId)
        registerPage.inputEmailPwd(mail, pwd)
        registerPage.inputPassCode(captcha)
        commonPage.findFriend()
        Assert.assertTrue(commonPage.checkTitle("好友"))
    }

    @When("M> Add friend with Name:{string}")
    @Throws(Exception::class)
    fun addFriendTest(friendName:String) {
        if(!friendPage.checkFriend(friendName)) {
            friendPage.addFriend(friendName)
            Assert.assertTrue("加入失敗", commonPage.checkTitle("尋找朋友"))
            commonPage.back(2)
        }else{
            println("已經加入好友$friendName")
        }
    }

    @Then("M> Send message with Name:{string}")
    @Throws(Exception::class)
    fun sendTest(friendName:String) {
        friendPage.choiceFriend(friendName)
        sendMessageTest()
        messagePage.withdrawMessage()
        swipeStickerTest()
        sendPhotoTest()
        sendVideoTest()

        //messagePage.shareMessage()
        //messagePage.forwardMessage()
        //messagePage.citeMessage()
        //messagePage.deleteMessage()

    }
    @Then("M> Block friend")
    @Throws(Exception::class)
    fun blockTest() {
        messagePage.block()
        Assert.assertTrue(messagePage.isBlock())
        messagePage.unBlock()
        Assert.assertTrue(messagePage.isUnBlock())
    }

    @After
    fun tearDown(scenario: Scenario) {
        ori.tearDown(this::class.java.packageName.split(".")[2]+"-" + scenario.id.substring(0,7))
    }

    private fun clickGroupTest(name:String):Unit {
        setUp()
        messagePage.findMsgPerson(name = name)
        val title = messagePage.getContext()
        Assert.assertTrue("$title and $name",title == name)
    }

    private fun sendMessageTest() {
       messagePage.sendMessage("Hello")
        val status = messagePage.checkLastMessage()
        Assert.assertTrue(status == "已傳送" || status == "讀取")
    }

    private fun swipeStickerTest():Unit {
        messagePage.chooseSticker(1)
        val time = messagePage.getContent()
        val formatDateTime = DateTimeFormatter.ofPattern("hh:mm")
        Assert.assertTrue (LocalTime.now().format(formatDateTime),time.split(" ")[0] == LocalTime.now().format(formatDateTime))
    }
    private fun sendPhotoTest():Unit {
        messagePage.sendPhoto()
        val status = messagePage.checkLastMessage()
        Assert.assertTrue(status == "已傳送" || status == "讀取")
    }
    private fun sendVideoTest():Unit {
        messagePage.sendVideo()
        //缺assert
    }

}