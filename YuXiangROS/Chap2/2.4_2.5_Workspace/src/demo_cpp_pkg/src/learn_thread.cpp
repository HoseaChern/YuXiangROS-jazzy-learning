#include <chrono>
#include <functional>
#include <httplib.h>
#include <iostream>
#include <thread>

class Download {
  private:
    std::mutex cout_mutex_; // 用于保护cout输出的互斥锁

  public:
    void download(
        const std::string& host, const std::string& path,
        const std::function<void(const std::string&, const std::string&, const std::string&)>&
            callback
    ) {
        {
            // 作用域锁: cout是非线程安全的, 需要加锁
            std::lock_guard<std::mutex> lock(cout_mutex_);
            std::cout << "Thread: " << std::this_thread::get_id() << " is downloading " << host
                      << path << std::endl;
        } // lock_guard 在作用域结束后自动释放锁, {}为保护作用域
        httplib::Client client(host);
        auto response = client.Get(path);
        if (response && response->status == 200) {
            {
                std::lock_guard<std::mutex> lock(cout_mutex_);
                callback(host, path, response->body);
            }
        }
    } // 对callback应用了函数装饰器

    void start_download(
        const std::string& host, const std::string& path,
        const std::function<void(const std::string&, const std::string&, const std::string&)>&
            callback
    ) {
        std::thread download_thread(&Download::download, this, host, path, callback);
        download_thread.detach();
    }
};

int main() {
    Download downloader;
    auto finish_callback =
        [](const std::string& host, const std::string& path, const std::string& content) -> void {
        std::cout << "Thread: " << std::this_thread::get_id() << " has downloaded " << host << path
                  << std::endl;
        std::cout << "Content: " << content << std::endl;
    }; // 匿名函数

    downloader.start_download("http://0.0.0.0:8000", "/novel1.txt", finish_callback);
    downloader.start_download("http://0.0.0.0:8000", "/novel2.txt", finish_callback);
    downloader.start_download("http://0.0.0.0:8000", "/novel3.txt", finish_callback);

    std::this_thread::sleep_for(std::chrono::seconds(5));

    return 0;
}