"""Constants of the Xiaomi Aqara Lock."""

WITH_LI_BATTERY = 1
SUPPORT_ALARM = 2
SUPPORT_DOORBELL = 4
SUPPORT_CAMERA = 8
SUPPORT_WIFI = 16

DEVICE_MAPPINGS = {
    "lumi.lock.aq1": SUPPORT_ALARM,
    "lumi.lock.acn02": SUPPORT_ALARM | SUPPORT_DOORBELL,
    "lumi.lock.acn03": SUPPORT_ALARM | SUPPORT_DOORBELL,
    "aqara.lock.eicn01": SUPPORT_ALARM | SUPPORT_DOORBELL,
    "aqara.lock.acn001": SUPPORT_ALARM | SUPPORT_DOORBELL,
    "aqara.lock.aqgl01": SUPPORT_ALARM | SUPPORT_DOORBELL,
    "aqara.lock.acn004": (
        WITH_LI_BATTERY | SUPPORT_ALARM |
        SUPPORT_DOORBELL | SUPPORT_WIFI),
    "aqara.lock.acn005": (
        WITH_LI_BATTERY | SUPPORT_ALARM |
        SUPPORT_DOORBELL | SUPPORT_WIFI),
    "aqara.lock.wbzac1": (
        WITH_LI_BATTERY | SUPPORT_ALARM |
        SUPPORT_DOORBELL | SUPPORT_WIFI | SUPPORT_CAMERA),
    "aqara.lock.bzacn3": (
        SUPPORT_ALARM | SUPPORT_DOORBELL),
    "aqara.lock.bzacn4": (
        SUPPORT_ALARM | SUPPORT_DOORBELL),
    "aqara.lock.dacn03": (
        WITH_LI_BATTERY | SUPPORT_ALARM |
        SUPPORT_DOORBELL | SUPPORT_WIFI | SUPPORT_CAMERA),
    "aqara.lock.acn002": (
        WITH_LI_BATTERY | SUPPORT_ALARM |
        SUPPORT_DOORBELL | SUPPORT_WIFI | SUPPORT_CAMERA),
    "aqara.lock.agl002": SUPPORT_ALARM | SUPPORT_DOORBELL,
    "aqara.lock.acn10": SUPPORT_ALARM
}

LOCK_NOTIFICATION = {
    "latch_state": {
        "default": "Latch state changed",
        "0": "解除反锁",  # "Remove the locking from inside",
        "1": "开启反锁",  # "Reverse locked",
    },
    "lock": {
        "default": "Lock state changed",
        "0": "门已开",  # "Door is open",
        "1": "门已关",  # "Door is closed",
        "2": "门未关",  # "Door is not close",
        "3": "有人按门铃",  # "Doorbell is ringing",
        "4": "门锁被破坏",  # "Lock is damaged",
        "5": "门虚掩",  # "Door is conceal",
        "6": "Other 1",
        "7": "Other 2"},
    # "door": {
    #     "default": "door state changed",
    #     "0": "Unknown",
    #     "1": "无法上锁",  # "The door cannot be locked",
    #     "2": "已开门",  # "The door is not closed", 0---
    #     "3": "未上锁",  # "The door is not locked", 1100
    #     "4": "已上锁",  # "The door is locked", 1110
    #     "5": "已反锁",  # "The door is auti-locked", ++01
    #     "6": "已开锁",  # "The door is unlocked", 10??
    #     "7": "已上锁且反锁",  # "The door is locked and auti-locked", ++11
    #     "8": "仍然开锁",  # "The door is left unlocked" +---
    # },
    "lock_event": {
        "default": "Got lock event",
        "0": "Unlock",
        "1": "Lock"
    },
    "unlock from inside": {
        "default": "Unlock from Inside",
        "0": "室内开锁",
    },
    "someone detected": {"default": "Someone is lingering at the door"},
    "li battery notify":
        {"default": "Li Battery notify",
            "0": "Li Battery is abnormal",
            "1": "Li Battery is normal"},
    # "battery notify":
    #     {"default": "Battery notify",
    #         "0": "Battery is die",
    #         "1": "Battery level is low",
    #         "2": "Battery level is middle",
    #         "3": "Battery level is full"},
    "camera connected": {"default": "Camera is connected"},
    "open in away mode": {
        "default":
            "In the Away-from-home Mode, someone opens the door indoors"},
    "lock by handle": {
        "default": "Lock by door handle",
        "0": "解除方锁",
        "1": "上提把手锁门",
    },
    "auto locking": {
        "default": "自动上锁状态改变",
        "1": "自动上锁",
    },
    "unlock by password": {
        "default": "密码开锁",  # "Unlocked with Keypad by user"
    },
    "unlock by fingerprint": {
        "default": "指纹开锁",  # "Unlocked with Fingerprint by user"
    },
    "unlock by bluetooth": {
        "default": "蓝牙开锁",  # "Unlocked with Bluetooth by user"
    },
    "unlock by homekit": {
        "default": "Unlocked with HomeKit by user",
        "0": "Aqara Home 蓝牙开锁",
        "2": "HomeKit开锁",
    },
    "unlock by key": {
        "default": "钥匙或应急旋钮开锁",  # "Unlocked with key by user"
    },
    "unlock by nfc": {
        "default": "NFC开锁",  # "Unlocked with NFC by user"
    },
    "unlock by face": {
        "default": "人脸开锁",  # "Unlocked with Face by user"
    },
    "unlock by temporary password": {
        "default": "一次性密码开锁",  # "Unlocked with Temporary Password"
    },
    # "key_type": {
    #     "default": "正常的开锁验证通过",
    #     "0": "指纹开锁",
    #     "1": "密码开锁",
    #     "3": "蓝牙开锁",
    #     "4": "一次性密码开锁",
    #     "5": "钥匙或应急旋钮开锁",
    #     "8": "HomeKit开锁",
    #     "9": "人脸开锁",
    # },
    "away mode": {
        "default": "Away mode changed",
        "0": "离家模式已解除",  # "Away-from-home mode is removed",
        "1": "离家模式已开启",  # "Away-from-home mode is enabled",
    },
    "nfc added": {"default": "Added NFC card or Tag"},
    "nfc removed": {"default": "Removed NFC card or Tag"},
    "verification failed": {
        "default": "门锁验证失败",  # "door lock verifications failed",
        "3235774464": "Frequent door opening failures due to incorrect passwords",
        "3235774465": "Frequent door opening failures due to incorrect fingerprints",
        "3235774469": "Frequent door openings with abnormal keys",
        "3235774470": "Foreign objects in the keyhole",
        "3235774471": "Keys not removed",
        "3235774472": "Frequent door opening failures with incorrect NFC",
        "3235774473": "Door unlocked after timeout",
        "3235774474": "Multiple verification failures (advanced protection)",
        "3235778564": "Automatic lock body abnormal"},
    "user added": {
        "default": "Add User"},
    "user removed": {
        "default": "Remove User"},
    "all user removed": {
        "default": "Remove All User"},
}
