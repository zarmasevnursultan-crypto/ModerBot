from datetime import datetime, timedelta, timezone

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    ChatPermissions,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.exceptions import TelegramBadRequest

from database import (
    add_warning,
    close_report,
    create_report,
    get_report,
)

router = Router()


def report_keyboard(report_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🗑 Удалить",
                    callback_data=f"report_action:delete:{report_id}",
                ),
                InlineKeyboardButton(
                    text="⚠️ Предупредить",
                    callback_data=f"report_action:warn:{report_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔇 Мут на 1 час",
                    callback_data=f"report_action:mute:{report_id}",
                ),
                InlineKeyboardButton(
                    text="🚫 Забанить",
                    callback_data=f"report_action:ban:{report_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отклонить",
                    callback_data=f"report_action:reject:{report_id}",
                )
            ],
        ]
    )


async def is_admin(message_or_callback) -> bool:
    member = await message_or_callback.bot.get_chat_member(
        message_or_callback.message.chat.id
        if isinstance(message_or_callback, CallbackQuery)
        else message_or_callback.chat.id,
        message_or_callback.from_user.id,
    )

    return member.status in ("administrator", "creator")


@router.message(Command("report"))
async def report_command(message: Message):
    if message.chat.type == "private":
        await message.answer(
            "❌ Жалобы работают только в группах."
        )
        return

    if not message.reply_to_message:
        await message.answer(
            "❌ Ответьте командой /report на сообщение нарушителя.\n\n"
            "Пример:\n"
            "/report оскорбление"
        )
        return

    reported_message = message.reply_to_message
    reported_user = reported_message.from_user

    if not reported_user:
        await message.answer(
            "❌ Не удалось определить автора сообщения."
        )
        return

    if reported_user.id == message.from_user.id:
        await message.answer(
            "❌ Нельзя пожаловаться на самого себя."
        )
        return

    if reported_user.is_bot:
        await message.answer(
            "❌ Нельзя пожаловаться на бота."
        )
        return

    reported_member = await message.bot.get_chat_member(
        message.chat.id,
        reported_user.id,
    )

    if reported_member.status in ("administrator", "creator"):
        await message.answer(
            "❌ Нельзя отправить жалобу на администратора."
        )
        return

    command_parts = message.text.split(maxsplit=1)

    if len(command_parts) == 2:
        reason = command_parts[1][:200]
    else:
        reason = "Причина не указана"

    report_id = await create_report(
        chat_id=message.chat.id,
        message_id=reported_message.message_id,
        reported_user_id=reported_user.id,
        reporter_user_id=message.from_user.id,
        reason=reason,
    )

    # Удаляем команду /report, чтобы не показывать автора жалобы
    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    await message.bot.send_message(
        chat_id=message.chat.id,
        text=(
            f"🚨 <b>Новая жалоба №{report_id}</b>\n\n"
            f"👤 Нарушитель: "
            f"<a href=\"tg://user?id={reported_user.id}\">"
            f"{reported_user.full_name}</a>\n"
            f"📝 Причина: {reason}\n\n"
            f"🔒 Автор жалобы скрыт.\n"
            f"Решение может принять только администратор."
        ),
        reply_to_message_id=reported_message.message_id,
        reply_markup=report_keyboard(report_id),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("report_action:"))
async def report_action(callback: CallbackQuery):
    if not await is_admin(callback):
        await callback.answer(
            "Эти кнопки доступны только администраторам.",
            show_alert=True,
        )
        return

    _, action, report_id_text = callback.data.split(":")
    report_id = int(report_id_text)

    report = await get_report(report_id)

    if report is None:
        await callback.answer(
            "Жалоба не найдена.",
            show_alert=True,
        )
        return

    chat_id, message_id, user_id, reason, status = report

    if status != "pending":
        await callback.answer(
            "Эта жалоба уже обработана.",
            show_alert=True,
        )
        return

    if callback.message.chat.id != chat_id:
        await callback.answer(
            "Неверная группа.",
            show_alert=True,
        )
        return

    result_text = ""

    try:
        if action == "delete":
            try:
                await callback.bot.delete_message(
                    chat_id=chat_id,
                    message_id=message_id,
                )
                result_text = "🗑 Сообщение удалено."
            except TelegramBadRequest:
                result_text = "ℹ️ Сообщение уже было удалено."

        elif action == "warn":
            warnings = await add_warning(chat_id, user_id)

            result_text = (
                f"⚠️ Пользователю выдано предупреждение.\n"
                f"Всего предупреждений: {warnings}."
            )

            if warnings >= 3:
                until_date = (
                    datetime.now(timezone.utc)
                    + timedelta(minutes=40)
                )

                await callback.bot.restrict_chat_member(
                    chat_id=chat_id,
                    user_id=user_id,
                    permissions=ChatPermissions(
                        can_send_messages=False
                    ),
                    until_date=until_date,
                )

                result_text += "\n🔇 После трёх предупреждений выдан мут на 40 минут."

        elif action == "mute":
            until_date = (
                datetime.now(timezone.utc)
                + timedelta(hours=1)
            )

            await callback.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=ChatPermissions(
                    can_send_messages=False
                ),
                until_date=until_date,
            )

            result_text = "🔇 Пользователь получил мут на 1 час."

        elif action == "ban":
            await callback.bot.ban_chat_member(
                chat_id=chat_id,
                user_id=user_id,
            )

            result_text = "🚫 Пользователь заблокирован."

        elif action == "reject":
            result_text = "❌ Жалоба отклонена."

        else:
            await callback.answer(
                "Неизвестное действие.",
                show_alert=True,
            )
            return

    except TelegramBadRequest as error:
        await callback.answer(
            f"Telegram не выполнил действие: {error.message}",
            show_alert=True,
        )
        return

    await close_report(report_id, action)

    admin_name = callback.from_user.full_name

    await callback.message.edit_text(
        callback.message.html_text
        + "\n\n"
        + result_text
        + f"\n👮 Решение принял: {admin_name}",
        parse_mode="HTML",
        reply_markup=None,
    )

    await callback.answer("Готово!")