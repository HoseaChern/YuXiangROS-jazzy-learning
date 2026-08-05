#include <QApplication> // 应用类
#include <QLabel>       // 显示文本
#include <QString>      // 存储字符串

int main(int argc, char* argv[]) {
    QApplication app(argc, argv);
    QLabel* label = new QLabel();
    QString msg = QString::fromStdString("Hello, World!");
    label->setText(msg);
    label->show();
    app.exec(); // 轮询
    return 0;
}
