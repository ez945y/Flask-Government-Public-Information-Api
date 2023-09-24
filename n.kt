package com.taiwanmobile.mplusapp.ui.gift.fragment

import android.app.AlertDialog
import android.content.Context
import android.os.Bundle
import android.text.TextUtils
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.EditText
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import com.mplusapp.R
import com.mplusapp.databinding.FragmentSendGiftCardBinding
import com.taiwanmobile.mplusapp.global.component.MPlusLog
import com.taiwanmobile.mplusapp.global.component.MPlusLog.d
import com.taiwanmobile.mplusapp.global.component.MPlusLog.e
import com.taiwanmobile.mplusapp.global.component.MPlusLog.i
import com.taiwanmobile.mplusapp.global.component.SystemConstant
import com.taiwanmobile.mplusapp.global.module.ChatModule
import com.taiwanmobile.mplusapp.manager.main.MemberManager
import com.taiwanmobile.mplusapp.model.main.Member
import com.taiwanmobile.mplusapp.ui.chatroom.fragment.ChatRoomFragment
import com.taiwanmobile.mplusapp.ui.gift.component.SendGiftObject
import com.taiwanmobile.mplusapp.ui.gift.manager.SendGiftManager
import com.taiwanmobile.mplusapp.ui.gift.viewmodel.SendGiftCardViewModel
import com.taiwanmobile.mplusapp.utils.AndroidUtil
import com.taiwanmobile.mplusapp.utils.Tools
import com.taiwanmobile.mplusapp.utils.UIUtil
import com.taiwanmobile.mplusapp.utils.system.Email
import kotlinx.coroutines.launch

class SendGiftCardFragment : Fragment() {
    private var _viewBinding: FragmentSendGiftCardBinding? = null
    private val viewBinding: FragmentSendGiftCardBinding get() = _viewBinding!!
    private val viewModel: SendGiftCardViewModel by viewModels()
    private var sendGiftObject: SendGiftObject? = null
    override fun onCreate(savedInstanceState: Bundle?) {
        i(TAG, "onCreate")
        super.onCreate(savedInstanceState)
        sendGiftObject = SendGiftManager.getInstance().sendGiftObject
    }

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?,
    ): View {
        i(TAG, "onCreateView")
        _viewBinding = FragmentSendGiftCardBinding.inflate(inflater, container, false)
        return viewBinding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        i(TAG, "onViewCreated")
        super.onViewCreated(view, savedInstanceState)
        viewBinding.directSendButton.setOnClickListener(directSendClickListener)
        viewBinding.writeMsgButton.setOnClickListener(writeMsgClickListener)
        bindLiveData()
    }

    fun bindLiveData() {
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.CREATED) {
                viewModel.deleteMemberState.collect {
                    viewBinding.directSendButton.isEnabled = true
                    if (it) {
                        progressDialog(
                            true, R.string.delMemberSendFreeSmsOK
                        )
                    } else {
                        progressDialog(false, R.string.delMemberSendFreeSmsError)
                    }
                }
            }
        }
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.CREATED) {
                viewModel.contactPersonState.collect {
                    viewBinding.directSendButton.isEnabled = true
                    if (it) {
                        progressDialog(true, R.string.sendSMSOK)
                    } else {
                        progressDialog(false, R.string.youCanReSendSMSInSendGiftInfo)
                    }
                }
            }
        }
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.CREATED) {
                viewModel.updateMessageState.collect {
                    if (MPlusLog.IS_DEBUG) {
                        d(TAG, "apiResult $it")
                    }
                }
            }
        }
        viewModel.giftCardPath.observe(viewLifecycleOwner) {
            viewBinding.giftCardLayout.messageEditText.isCursorVisible = true
            if (it != null) {
                val resultList = java.util.ArrayList<String>()
                resultList.add(it)
                giftCardPathOnSuccess(arrayListOf(it))
            } else {
                giftCardPathOnError()
            }
            viewBinding.directSendButton.isEnabled = true
        }
    }

    override fun onDestroy() {
        i(TAG, "onDestroy")
        super.onDestroy()
    }

    override fun onPause() {
        i(TAG, "onPause")
        super.onPause()
    }

    override fun onResume() {
        i(TAG, "onResume")
        super.onResume()
        UIUtil.hideBottomBar(activity)
    }

    override fun onStart() {
        i(TAG, "onStart")
        super.onStart()
    }

    override fun onStop() {
        i(TAG, "onStop")
        super.onStop()
    }

    override fun onDestroyView() {
        i(TAG, "onDestroyView")
        super.onDestroyView()
    }

    override fun onDetach() {
        i(TAG, "onDetach")
        super.onDetach()
    }

    private val message: String
        get() {
            val receiverId = sendGiftObject?.receiverId
            var sendMember: Member? = null
            if (!Tools.isNullOrEmpty(receiverId)) {
                sendMember = MemberManager.getInstance().getMemberByUserId(activity, receiverId)
            } else {
                d(TAG, "receiverMsisdn[" + sendGiftObject?.receiverMsisdn + "]")
            }
            val message: String
            if (sendMember != null) {
                val name = sendMember.serverNickName
                if (MPlusLog.IS_DEBUG) {
                    d(TAG, "name[$name]")
                }
                message = if (name.length > 8) {
                    (requireActivity().getString(R.string.dear) + SystemConstant.SPACE +
                            name + SystemConstant.COMMA + "\r\n" +
                            requireActivity().getString(R.string.sendGiftToU2))
                } else {
                    (requireActivity().getString(R.string.dear) + SystemConstant.SPACE +
                            name + SystemConstant.COMMA + "\r\n" +
                            requireActivity().getString(R.string.sendGiftToU))
                }
            } else {
                if (MPlusLog.IS_DEBUG) {
                    d(TAG, "sendMember is null")
                }
                message = (requireActivity().getString(R.string.dear) + SystemConstant.SPACE +
                        sendGiftObject?.receiverName + SystemConstant.COMMA + "\r\n" +
                        requireActivity().getString(R.string.sendGiftToU))
            }
            return message
        }

    private fun setProgressDialogVisible(visible: Int) {
        try {
            if (visible == View.VISIBLE) {
                d(TAG, "OPEN_PROGRESS")
                viewBinding.progressBar.root.visibility = View.VISIBLE
            } else {
                viewBinding.progressBar.root.visibility = View.GONE
            }
        } catch (e: Exception) {
            e(e)
        }
    }


    private val directSendClickListener: View.OnClickListener = object : View.OnClickListener {
        override fun onClick(v: View) {
            try {
                if (MPlusLog.IS_DEBUG) {
                    d("directSendClickListener")
                }
                if (!Tools.isNetworkOK(activity)) {
                    val builder = AlertDialog.Builder(activity)
                    builder.setCancelable(false)
                    builder.setTitle(R.string.app_name)
                    builder.setMessage(R.string.noNetwork)
                    builder.setPositiveButton(R.string.confirm, null)
                    builder.create()
                    builder.show()
                    return
                }
                setProgressDialogVisible(View.VISIBLE)
                val message: String = message
                sendGiftObject?.cardMessage = message
                if (!TextUtils.isEmpty(sendGiftObject?.cardMessage)) {
                    viewModel.updateMessageAsyncTask(requireActivity(), sendGiftObject)
                }
                if (TextUtils.isEmpty(sendGiftObject?.receiverId)) {
                    if (MPlusLog.IS_DEBUG) {
                        d(TAG, "送給聯絡人朋友[" + sendGiftObject?.receiverMsisdn + "]")
                    }
                    v.isEnabled = false
                    viewModel.smsAsyncTask(
                        requireActivity(),
                        isDelete = false,
                        isSendNow = true,
                        hasLeaveMsg = !TextUtils.isEmpty(message),
                        msisdn = sendGiftObject?.receiverMsisdn,
                        serialNo = sendGiftObject?.serialNo,
                        contentName = sendGiftObject?.contentName,
                        expiredDate = sendGiftObject?.exchange_date
                    )

                } else {
                    val userId = sendGiftObject?.receiverId
                    val isDelete =
                        MemberManager.getInstance().isExistedInDeleteMember(activity, userId)
                    if (isDelete) {
                        if (MPlusLog.IS_DEBUG) {
                            d(TAG, "帳號已刪除[" + sendGiftObject?.receiverMsisdn + "]")
                        }
                        if (!TextUtils.isEmpty(sendGiftObject?.receiverMsisdn)) {
                            if (MPlusLog.IS_DEBUG) {
                                d(TAG, "有門號")
                            }
                            v.isEnabled = false
                            viewModel.smsAsyncTask(
                                requireActivity(),
                                isDelete = true,
                                isSendNow = true,
                                hasLeaveMsg = !TextUtils.isEmpty(message),
                                msisdn = sendGiftObject?.receiverMsisdn,
                                serialNo = sendGiftObject?.serialNo,
                                contentName = sendGiftObject?.contentName,
                                expiredDate = sendGiftObject?.exchange_date
                            )
                            //sendGiftToDeleteMemberCallBack
                        } else {
                            if (MPlusLog.IS_DEBUG) {
                                d(TAG, "無門號")
                            }
                            val builder = AlertDialog.Builder(activity)
                            builder.setCancelable(false)
                            builder.setTitle(R.string.app_name)
                            builder.setMessage(R.string.delMemberAndNoPhone)
                            builder.setPositiveButton(R.string.confirm) { dialog, which ->
                                AndroidUtil.startFragment(
                                    parentFragmentManager, GiftListFragment::class.java,
                                    R.id.fragmentArea, null
                                )
                            }
                            builder.setNegativeButton(
                                R.string.serviceEmail
                            ) { dialog, which ->
                                val giftMail = arrayOf(SystemConstant.FEEDBACK_MAIL)
                                Email.feedBack(
                                    activity,
                                    requireActivity().getString(R.string.feedBackTitle),
                                    giftMail,
                                    arrayOf(),
                                    false
                                )
                                AndroidUtil.startFragment(
                                    parentFragmentManager, GiftListFragment::class.java,
                                    R.id.fragmentArea, null
                                )
                            }
                            builder.create()
                            builder.show()
                        }
                    } else {
                        if (MPlusLog.IS_DEBUG) {
                            d(TAG, "M+用戶")
                        }
                        if (sendGiftObject != null) {
                            sendGiftCardMsgAsyncTask(
                                requireActivity(),
                                viewBinding.giftCardLayout.root,
                                sendGiftObject!!,
                                sendGiftObject!!.cardMessage,
                                v
                            )
                        }
                    }
                }
            } catch (e: Exception) {
                e(e)
            }
        }
    }

    private fun sendGiftCardMsgAsyncTask(
        context: Context,
        giftCardView: View,
        sendGiftObject: SendGiftObject,
        message: String,
        sendBtn: View,
    ) {
        sendBtn.isEnabled = false
        val giftNameText = giftCardView.findViewById<TextView>(R.id.giftNameText)
        val expireTimeText = giftCardView.findViewById<TextView>(R.id.expireTimeText)
        val messageEditText = giftCardView.findViewById<EditText>(R.id.messageEditText)
        giftNameText.text = sendGiftObject.contentName
        expireTimeText.text = sendGiftObject.exchange_date
        messageEditText.setText(message)
        messageEditText.isCursorVisible = false
        giftCardView.visibility = View.VISIBLE
        viewModel.sendGiftCardMsgAsyncTask(context, giftCardView, sendGiftObject)
    }

    private val writeMsgClickListener: View.OnClickListener = View.OnClickListener {
        try {
            if (MPlusLog.IS_DEBUG) d("writeMsgClickListener")
            AndroidUtil.startFragment(
                parentFragmentManager, GiftCardEditMessageFragment::class.java,
                R.id.fragmentArea, null
            )
        } catch (e: Exception) {
            e(e)
        }
    }

    fun progressDialog(isSuccess: Boolean, msg: Int) {
        if (MPlusLog.IS_DEBUG) {
            if (isSuccess) {
                d(TAG, "onSuccess")
            } else {
                d(TAG, "onError")
            }
        }
        setProgressDialogVisible(View.GONE)
        val builder = AlertDialog.Builder(activity)
        builder.setCancelable(false)
        builder.setTitle(R.string.app_name)
        builder.setMessage(msg)
        builder.setPositiveButton(
            R.string.confirm
        ) { dialog, which ->
            AndroidUtil.startFragment(
                parentFragmentManager, GiftListFragment::class.java,
                R.id.fragmentArea, null
            )
        }
        builder.create()
        builder.show()
    }

    private fun giftCardPathOnSuccess(successData: ArrayList<String>) {
        if (MPlusLog.IS_DEBUG) {
            d(TAG, "onSuccess")
        }
        setProgressDialogVisible(View.GONE)
        val giftCardPath = successData[0]
        ChatModule.sendGiftCardMessage(
            activity, sendGiftObject?.receiverId, giftCardPath,
            sendGiftObject?.serialNo, sendGiftObject?.exchange_date,
            sendGiftObject?.contentId, sendGiftObject?.cardMessage
        )
        if (MPlusLog.IS_DEBUG) {
            d(TAG, "go to chatRoom")
        }
        val manager = parentFragmentManager
        AndroidUtil.popupAllFragment(manager)
        val argument = Bundle()
        argument.putString(ChatRoomFragment.BUNDLE_KEY_USER_ID, sendGiftObject?.receiverId)
        argument.putInt(
            ChatRoomFragment.BUNDLE_KEY_BACK_TO_MODE,
            ChatRoomFragment.BACK_TO_MODE_CHAT_LIST
        )
        argument.putBoolean(ChatRoomFragment.BUNDLE_KEY_REQUEST_FROM_INSIDE, true)
        AndroidUtil.startFragment(
            manager,
            ChatRoomFragment::class.java,
            R.id.fragmentArea,
            argument
        )
    }

    private fun giftCardPathOnError() {
        if (MPlusLog.IS_DEBUG) {
            d(TAG, "onError")
        }
        setProgressDialogVisible(View.GONE)
        val builder = AlertDialog.Builder(activity)
        builder.setCancelable(false)
        builder.setTitle(R.string.app_name)
        builder.setMessage(R.string.alertGiftCardOOM)
        builder.setPositiveButton(
            R.string.confirm
        ) { dialogInterface, i ->
            val manager = parentFragmentManager
            AndroidUtil.popupAllFragment(manager)
            val argument = Bundle()
            argument.putString(
                ChatRoomFragment.BUNDLE_KEY_USER_ID,
                sendGiftObject?.receiverId
            )
            argument.putInt(
                ChatRoomFragment.BUNDLE_KEY_BACK_TO_MODE,
                ChatRoomFragment.BACK_TO_MODE_CHAT_LIST
            )
            argument.putBoolean(ChatRoomFragment.BUNDLE_KEY_REQUEST_FROM_INSIDE, true)
            AndroidUtil.startFragment(
                manager,
                ChatRoomFragment::class.java,
                R.id.fragmentArea,
                argument
            )
        }
        builder.create()
        builder.show()
    }
    companion object {
        private const val TAG = "SendGiftCardFragment"
    }
}