from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerEmpty
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
from telethon.tl.functions.channels import InviteToChannelRequest
import csv
import traceback
import time


api_id = 1038476
api_hash = 'c8e3a76798991d9efa731038409ebc55'
phone = str(input('Enter the phone number: '))
client = TelegramClient(phone, api_id, api_hash)


def connectClient():
    client.connect()
    if not client.is_user_authorized():
        client.send_code_request(phone)
        client.sign_in(phone, input('Enter the code: '))


def scrapeGroups():
    chats = []
    last_date = None
    chunk_size = 200
    groups = []

    result = client(GetDialogsRequest(
        offset_date=last_date,
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=chunk_size,
        hash=0
    ))
    chats.extend(result.chats)

    for chat in chats:
        try:
            if chat.megagroup == True:
                groups.append(chat)
        except:
            continue

    print('Choose a group to scrape members from:')
    i = 0
    for g in groups:
        print(str(i) + '- ' + g.title)
        i += 1

    g_index = input("Enter a Number: ")
    target_group = groups[int(g_index)]

    print('Fetching Members...')
    all_participants = []
    all_participants = client.get_participants(target_group, aggressive=True)
    usernames = []
    for participant in all_participants:
        if participant.username is not None:
            usernames.append(participant.username)
        else:
            usernames.append('User type is none')
    client.send_message(
        'me', f"List of all users From {target_group.title}.\n Total user count {len(usernames)}")
    client.send_message('me', "\n".join(usernames))
    # Adding to group
    print('Choose a group to add members:')
    i = 0
    for group in groups:
        print(str(i) + '- ' + group.title)
        i += 1

    g_index = input("Enter a Number: ")
    target_group = groups[int(g_index)]

    target_group_entity = InputPeerChannel(
        target_group.id, target_group.access_hash)

    for user in usernames:
        try:
            print("Adding {}".format(user))
            if user == "User type is none":
                continue
            user_to_add = client.get_input_entity(user)
            client(InviteToChannelRequest(
                target_group_entity, [user_to_add]))
            print("Waiting 60 Seconds...")
            time.sleep(60)
        except PeerFloodError:
            print(
                "Getting Flood Error from telegram. Script is stopping now. Please try again after some time.")
        except UserPrivacyRestrictedError:
            print("The user's privacy settings do not allow you to do this. Skipping.")
        except:
            traceback.print_exc()
            print("Unexpected Error")
            continue


def main():
    connectClient()
    scrapeGroups()
    print('Members scraped successfully.')


if __name__ == '__main__':
    main()
