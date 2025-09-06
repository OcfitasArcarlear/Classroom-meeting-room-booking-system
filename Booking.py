# booking_web.py
import streamlit as st
import pandas as pd

# ---------------- Models ----------------
class Room:
    def __init__(self, room_id, name, room_type, owner):
        self.room_id = room_id
        self.name = name
        self.room_type = room_type
        self.owner = owner      
        self.is_booked = False
        self.booked_by = None   

class User:
    def __init__(self, username):
        self.username = username

class HostUser(User):  
    def __init__(self, username):
        super().__init__(username)

class BookerUser(User):  
    def __init__(self, username):
        super().__init__(username)

class BookingSystem:
    def __init__(self):
        self.rooms = []

    def add_room(self, room):
        for r in self.rooms:
            if r.room_id == room.room_id:
                return False
        self.rooms.append(room)
        return True

    def remove_room(self, room_id, host_user):
        for room in self.rooms:
            if room.room_id == room_id and room.owner.username == host_user.username:
                if room.is_booked:
                    return False
                self.rooms.remove(room)
                return True
        return False

    def get_all_rooms(self):
        return self.rooms

    def search_rooms(self, keyword):
        return [room for room in self.rooms if keyword.lower() in room.name.lower()]

    def book_room(self, room_id, booker):
        for room in self.rooms:
            if room.room_id == room_id and not room.is_booked:
                room.is_booked = True
                room.booked_by = booker
                return True
        return False

    def cancel_booking(self, room_id, booker):
        for room in self.rooms:
            if room.room_id == room_id and room.is_booked and room.booked_by.username == booker.username:
                room.is_booked = False
                room.booked_by = None
                return True
        return False

# ---------------- Streamlit App ----------------
st.set_page_config(page_title="ระบบจองห้อง", layout="wide")

if "system" not in st.session_state:
    st.session_state.system = BookingSystem()
    # Sample data
    host1 = HostUser("อาจารย์ ก")
    host2 = HostUser("อาจารย์ ข")
    st.session_state.system.add_room(Room("101", "ห้องเรียนใหญ่ อาคาร A", "ห้องเรียน", host1))
    st.session_state.system.add_room(Room("102", "ห้องประชุมเล็ก อาคาร B", "ห้องประชุม", host2))
    st.session_state.system.add_room(Room("201", "ห้องปฏิบัติการคอมพิวเตอร์", "แล็บ", host1))
    st.session_state.system.add_room(Room("301", "ห้องสมุดกลาง", "ห้องสมุด", host2))

system = st.session_state.system

st.title("ระบบจองห้อง (Host / Booker)")

# Sidebar: Search and Add Room
st.sidebar.header("ค้นหาห้อง")
keyword = st.sidebar.text_input("ชื่อห้อง:")
if st.sidebar.button("ค้นหา"):
    rooms = system.search_rooms(keyword)
else:
    rooms = system.get_all_rooms()

st.sidebar.header("สร้างห้องใหม่")
with st.sidebar.form("create_room_form"):
    new_id = st.text_input("รหัสห้อง")
    new_name = st.text_input("ชื่อห้อง")
    new_type = st.text_input("ประเภท")
    host_name = st.text_input("ชื่อ Host")
    submitted = st.form_submit_button("สร้างห้อง")
    if submitted:
        if not new_id or not new_name or not new_type or not host_name:
            st.warning("กรุณากรอกข้อมูลให้ครบ")
        else:
            host = HostUser(host_name)
            if system.add_room(Room(new_id, new_name, new_type, host)):
                st.success(f"{host.username} สร้างห้อง {new_id} เรียบร้อยแล้ว")
                st.rerun()
            else:
                st.error("รหัสห้องนี้มีอยู่แล้ว")

# ---------------- Room Table ----------------
st.subheader("รายการห้อง")
room_data = []
for room in rooms:
    status = f"📌 จองโดย {room.booked_by.username}" if room.is_booked else "✅ พร้อมใช้งาน"
    room_data.append([room.room_id, room.name, room.room_type, room.owner.username, status])

# ใช้ DataFrame เพื่อใส่ชื่อคอลัมน์
df = pd.DataFrame(room_data, columns=["รหัสห้อง", "ชื่อห้อง", "ประเภท", "Host", "สถานะ"])

# รีเซ็ต index ให้เรียง 1,2,3,...
df.index = range(1, len(df) + 1)

st.table(df)

# ---------------- Booking / Cancel ----------------
st.subheader("จอง / ยกเลิกห้อง")
cols = st.columns(2)
with cols[0]:
    booker_name = st.text_input("ชื่อผู้จอง", key="booker_name")
with cols[1]:
    selected_room = st.selectbox("เลือกห้อง", [room.room_id for room in system.get_all_rooms()])

booking_action = st.radio("การดำเนินการ", ["จองห้อง", "ยกเลิกการจอง"])
if st.button("ยืนยัน"):
    if not booker_name:
        st.warning("กรุณากรอกชื่อผู้จอง")
    else:
        booker = BookerUser(booker_name)
        if booking_action == "จองห้อง":
            if system.book_room(selected_room, booker):
                st.success(f"{booker.username} จองห้อง {selected_room} เรียบร้อยแล้ว")
                st.rerun()
            else:
                st.error("ห้องนี้ถูกจองแล้ว")
        else:
            if system.cancel_booking(selected_room, booker):
                st.success(f"{booker.username} ยกเลิกการจองห้อง {selected_room} แล้ว")
                st.rerun()
            else:
                st.error("ไม่สามารถยกเลิกการจองได้")

# ---------------- Delete Room ----------------
st.subheader("ลบห้อง")
host_del_name = st.text_input("ชื่อ Host สำหรับลบห้อง", key="host_del")
room_del = st.selectbox("เลือกห้องที่จะลบ", [room.room_id for room in system.get_all_rooms()], key="del_room")

if st.button("ลบห้อง"):
    if not host_del_name:
        st.warning("กรุณากรอกชื่อ Host")
    else:
        host = HostUser(host_del_name)
        if system.remove_room(room_del, host):
            st.success(f"ห้อง {room_del} ถูกลบเรียบร้อยแล้ว")
            st.rerun()
        else:
            # หาเจ้าของจริง ๆ ของห้อง เพื่อบอกสาเหตุ
            room_owner = None
            for r in system.get_all_rooms():
                if r.room_id == room_del:
                    room_owner = r.owner.username
                    break
            if room_owner and room_owner != host_del_name:
                st.error(f"ไม่สามารถลบห้องได้: เจ้าของห้องคือ {room_owner}")
            else:
                st.error("ไม่สามารถลบห้องได้ (อาจมีการจองอยู่)")
