from aiogram.fsm.state import State, StatesGroup

class GetReportFSM(StatesGroup):
    waiting_for_report = State()